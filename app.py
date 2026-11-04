import json
import os
import re
import hmac
import secrets
import logging
import time

from datetime import datetime, date, timedelta
from functools import wraps
from zoneinfo import ZoneInfo
from flask import (
    Flask, render_template, request, flash, redirect,
    session, abort, url_for, jsonify
)

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_database


# =========================================================
# 1. CONFIGURATION
# =========================================================

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"

def load_or_create_secret_key():
    """
    Keep Flask sessions valid across PythonAnywhere worker restarts.

    The generated key is stored outside the repository in Flask's instance
    directory with owner-only file permissions. An explicitly configured
    SECRET_KEY environment variable always takes precedence.
    """
    os.makedirs(app.instance_path, exist_ok=True)
    key_path = os.path.join(app.instance_path, "secret_key")

    try:
        file_descriptor = os.open(
            key_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError:
        secret_value = ""

        # Another WSGI worker may have created the file moments ago.
        for _ in range(50):
            try:
                with open(key_path, "r", encoding="utf-8") as key_file:
                    secret_value = key_file.read().strip()
            except FileNotFoundError:
                secret_value = ""

            if len(secret_value) >= 64:
                break

            time.sleep(0.02)
    else:
        secret_value = secrets.token_hex(32)

        with os.fdopen(file_descriptor, "w", encoding="utf-8") as key_file:
            key_file.write(secret_value)

    if len(secret_value) < 64:
        raise RuntimeError(
            "Flask could not load a persistent SECRET_KEY. "
            "Set SECRET_KEY in the server environment."
        )

    try:
        os.chmod(key_path, 0o600)
    except OSError:
        app.logger.warning("Could not restrict permissions on the session key file.")

    return secret_value


secret_key = os.getenv("SECRET_KEY") or load_or_create_secret_key()

app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    SESSION_REFRESH_EACH_REQUEST=True,
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)

logging.basicConfig(level=logging.INFO)


# =========================================================
# 2. CONSTANTS
# =========================================================

BLOOD_TYPES = {
    "O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"
}

URGENCY_LEVELS = {"Normal", "Emergency"}

AVAILABLE = "Available"
UNAVAILABLE = "Not Available"

ACTIVE_MATCH_STATUSES = (
    "Accepted",
    "Confirmed",
    "Donation Reported",
)

BLOOD_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}

HEALTH_QUESTIONS = {
    "fever": "Have you had a fever or serious infection recently?",
    "chronic_condition": "Do you have a medical condition that may affect donation?",
    "medication": "Are you currently taking medication that may affect donation?",
    "recent_surgery": "Have you recently had surgery or a major medical procedure?",
    "blood_condition": "Have you been diagnosed with a blood-related condition?",
}


# =========================================================
# 3. GENERAL HELPERS
# =========================================================

PAKISTAN_TZ = ZoneInfo("Asia/Karachi")


def get_user_id():
    """Return the authenticated user's ID, or None for public visitors."""
    return session.get("user_id")


def get_current_time():
    """Return the current Pakistan local time in database-safe format."""
    return get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S")


def get_pakistan_time():
    """Return the current timezone-aware Pakistan datetime."""
    return datetime.now(PAKISTAN_TZ)


def parse_date(value):
    """Parse a date value safely; return a date object or None."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except (TypeError, ValueError):
        return None


def clean_text(value):
    """Normalize user-supplied text without accepting non-string values."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def form_text(field_name, max_length=250):
    """Read and length-limit a cleaned form field."""
    value = clean_text(request.form.get(field_name, ""))
    return value[:max_length]


def valid_phone(value):
    """Accept common Pakistani/international phone-number formatting."""
    if not value:
        return False
    digits = re.sub(r"\D", "", str(value))
    return 10 <= len(digits) <= 15


def valid_email(value):
    """Basic email syntax validation."""
    if not value:
        return False
    email = str(value).strip()
    if email.count('@') != 1:
        return False
    local, domain = email.split('@', 1)
    return bool(local and '.' in domain and not domain.startswith('.') and not domain.endswith('.'))


def normalize_cnic(value):
    """Return a CNIC as 13 digits, or an empty string when invalid."""
    digits = re.sub(r"\D", "", str(value or ""))
    return digits if len(digits) == 13 else ""


def normalize_whatsapp_number(value):
    """Convert a Pakistani phone number to digits-only international format."""
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("0092"):
        digits = digits[2:]
    if digits.startswith("0") and len(digits) == 11:
        digits = "92" + digits[1:]
    elif len(digits) == 10 and digits.startswith("3"):
        digits = "92" + digits
    return digits


def get_compatible_donor_groups(recipient_blood_type):
    """Return donor blood groups compatible with the recipient's group."""
    return sorted(
        donor_type
        for donor_type, recipients in BLOOD_COMPATIBILITY.items()
        if recipient_blood_type in recipients
    )


def locations_match(first_location, second_location):
    """
    Compare donor and requester locations at city level.

    Accepts equivalent entries such as:
    - "Sukkur" and "Sukkur, Sindh"
    - "Sukkur, Sindh" and "Sukkur City"
    - "Gulshan-e-Iqbal, Karachi" and "DHA, Karachi"

    It deliberately compares complete location components instead of
    matching any shared word, which could create false positives.
    """
    administrative_terms = {
        "city", "district", "tehsil", "taluka", "division",
        "province", "sindh", "punjab", "balochistan",
        "khyber", "pakhtunkhwa", "kpk", "pakistan",
    }

    def normalize_component(value):
        tokens = re.findall(r"[a-z0-9]+", clean_text(value).lower())
        meaningful_tokens = [
            token for token in tokens
            if token not in administrative_terms
        ]
        return " ".join(meaningful_tokens).strip()

    def location_components(value):
        raw = clean_text(value)
        if not raw:
            return set()

        # Commas/slashes commonly separate the locality and city.
        parts = re.split(r"[,/|;]|\s+-\s+", raw)
        candidates = {
            normalize_component(part)
            for part in parts
            if normalize_component(part)
        }

        # Also compare the complete normalized entry after removing
        # province/country/administrative suffixes.
        whole = normalize_component(raw)
        if whole:
            candidates.add(whole)

        return candidates

    first = location_components(first_location)
    second = location_components(second_location)

    if not first or not second:
        return False

    return bool(first.intersection(second))


def donor_matches_request(
    donor_blood_type,
    donor_location,
    request_blood_type,
    request_location,
):
    """Return whether a donor can supply the requested group in the same city."""
    return (
        request_blood_type in BLOOD_COMPATIBILITY.get(donor_blood_type, [])
        and locations_match(donor_location, request_location)
    )


def get_notification_recipient_user_ids(
    donor_rows,
    request_blood_type,
    request_location,
    excluded_user_id=None,
):
    """Return unique user IDs for donors compatible with a blood request."""
    recipient_ids = []
    seen_user_ids = set()

    for donor_row in donor_rows:
        donor_user_id = donor_row[0]
        donor_blood_type = donor_row[1]
        donor_location = donor_row[2]
        if (
            not donor_user_id
            or donor_user_id == excluded_user_id
            or donor_user_id in seen_user_ids
        ):
            continue

        if donor_matches_request(
            donor_blood_type,
            donor_location,
            request_blood_type,
            request_location,
        ):
            recipient_ids.append(donor_user_id)
            seen_user_ids.add(donor_user_id)

    return recipient_ids


def get_inserted_id(cursor, connection):
    """Return the ID generated by the most recent INSERT."""
    inserted_id = getattr(cursor, "lastrowid", None)
    if inserted_id is not None:
        return inserted_id
    if hasattr(connection, "connection"):
        row = connection.execute("SELECT LASTVAL()").fetchone()
    else:
        row = connection.execute("SELECT last_insert_rowid()").fetchone()

    return row[0] if row else None


def record_audit(connection, user_id, action, entity_type, entity_id, details=None):
    """Write a lightweight audit entry within the caller's transaction."""
    connection.execute(
        """
        INSERT INTO audit_logs
            (user_id, action, entity_type, entity_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            entity_type,
            entity_id,
            clean_text(details) or None,
            get_current_time(),
        ),
    )


def parse_needed_by(value):
    """
    Parse a datetime-local value using Pakistan time.

    Expected input:
        YYYY-MM-DDTHH:MM

    Returns:
        (deadline_datetime, database_value, urgency)
        or (None, None, None) if invalid.
    """

    if not value or not isinstance(value, str):
        return None, None, None

    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None, None, None

    # datetime-local input must not contain a timezone or UTC offset.
    if parsed.tzinfo is not None:
        return None, None, None

    deadline = parsed.replace(tzinfo=PAKISTAN_TZ)
    now = get_pakistan_time()

    if deadline <= now:
        return None, None, None

    time_remaining = deadline - now

    urgency = (
        "Emergency"
        if time_remaining <= timedelta(hours=24)
        else "Normal"
    )

    database_value = deadline.strftime("%Y-%m-%d %H:%M:%S")

    return deadline, database_value, urgency


def parse_stored_deadline(value):
    """
    Read old and current ISO-formatted deadlines using Pakistan time.
    """

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(str(value).strip())

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=PAKISTAN_TZ)

        return parsed.astimezone(PAKISTAN_TZ)

    except (ValueError, TypeError):
        return None


def is_request_expired(needed_by):
    """
    Treat missing or invalid deadlines as unavailable for acceptance.
    """

    deadline = parse_stored_deadline(needed_by)

    if deadline is None:
        return True

    return deadline <= get_pakistan_time()


def calculate_request_reminder_time(created_at, needed_by):
    """Return the reminder point with 45% of the request duration remaining."""
    created = parse_stored_deadline(created_at)
    deadline = parse_stored_deadline(needed_by)
    if created is None or deadline is None or deadline <= created:
        return None
    return created + (deadline - created) * 0.55


# =========================================================
# 4. AUTHENTICATION


def login_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped


# =========================================================
# 5. CSRF PROTECTION
# =========================================================

def get_csrf_token():
    token = session.get("_csrf_token")

    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token

    return token


def get_unread_notification_count(user_id):
    """Return the current user's unread notification count."""
    if not user_id:
        return 0

    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT COUNT(*)
            FROM notifications
            WHERE user_id = ?
              AND is_read = 0
            """,
            (user_id,),
        ).fetchone()

        return int(row[0] or 0) if row else 0

    except Exception:
        app.logger.exception("Unread notification count could not be loaded")
        return 0

    finally:
        connection.close()


@app.context_processor
def inject_template_values():
    user_id = get_user_id()

    return {
        "csrf_token": get_csrf_token,
        "current_user_id": user_id,
        "blood_types": sorted(BLOOD_TYPES),
        "notification_unread_count": get_unread_notification_count(user_id),
    }


@app.before_request
def protect_state_changing_requests():
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return None

    session_token = session.get("_csrf_token")

    submitted_token = (
        request.form.get("csrf_token")
        or request.headers.get("X-CSRF-Token")
    )

    if (
        not session_token
        or not submitted_token
        or not hmac.compare_digest(
            str(session_token),
            str(submitted_token),
        )
    ):
        abort(400, description="Missing or invalid CSRF token.")

    return None


# =========================================================
# 6. SECURITY HEADERS
# =========================================================

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"

    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# =========================================================
# 7. NOTIFICATIONS
# =========================================================

def create_notification(
    connection,
    user_id,
    message,
    notification_type,
    related_request_id=None,
    related_match_id=None,
):
    if not user_id:
        return

    connection.execute(
        """
        INSERT INTO notifications
            (
                user_id, message, notification_type, created_at,
                related_request_id, related_match_id
            )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            message,
            notification_type,
            get_current_time(),
            related_request_id,
            related_match_id,
        ),
    )


def notify_requesters_of_compatible_donor(connection, donor_id):
    """
    Notify request owners when this donor profile becomes a live potential match.
    Duplicate alerts for the same donor profile/request are suppressed by message.
    """
    donor = connection.execute(
        """
        SELECT id, user_id, name, blood_type, location,
               availability, eligible, health_screening_status, last_donation
        FROM donors
        WHERE id = ?
        """,
        (donor_id,),
    ).fetchone()

    if not donor:
        return

    (
        donor_profile_id, donor_user_id, donor_name, donor_blood_type,
        donor_location, availability, eligible, health_status, last_donation,
    ) = donor

    if (
        not donor_user_id
        or availability != AVAILABLE
        or eligible != 1
        or health_status != "Self-Declared Clear"
    ):
        return

    cooldown_cutoff = (
        get_pakistan_time().date() - timedelta(days=90)
    ).isoformat()
    if last_donation and str(last_donation) > cooldown_cutoff:
        return

    active_match = connection.execute(
        """
        SELECT 1
        FROM request_matches
        WHERE donor_id = ?
          AND (status IN (?, ?, ?) OR status = 'Invited')
        LIMIT 1
        """,
        (donor_profile_id, *ACTIVE_MATCH_STATUSES),
    ).fetchone()
    if active_match:
        return

    now = get_pakistan_time()
    open_requests = connection.execute(
        """
        SELECT id, user_id, blood_type, location, needed_by
        FROM blood_requests
        WHERE status = 'Pending'
          AND remaining_units > 0
          AND needed_by IS NOT NULL
          AND needed_by > ?
          AND user_id != ?
        ORDER BY id DESC
        """,
        (
            now.strftime("%Y-%m-%d %H:%M:%S"),
            donor_user_id,
        ),
    ).fetchall()

    for blood_request in open_requests:
        request_id, requester_id, request_blood_type, request_location, needed_by = blood_request

        if not donor_matches_request(
            donor_blood_type,
            donor_location,
            request_blood_type,
            request_location,
        ):
            continue

        message = (
            f"A compatible donor has arrived: {donor_name} "
            f"({donor_blood_type}) is available for your "
            f"{request_blood_type} blood request #{request_id}. "
            "Open Potential Matches to review."
        )

        already_notified = connection.execute(
            """
            SELECT 1
            FROM notifications
            WHERE user_id = ?
              AND related_request_id = ?
              AND notification_type = 'compatible_donor'
              AND message = ?
            LIMIT 1
            """,
            (requester_id, request_id, message),
        ).fetchone()

        if not already_notified:
            create_notification(
                connection,
                requester_id,
                message,
                "compatible_donor",
                related_request_id=request_id,
            )


# =========================================================
# 8. DONOR ELIGIBILITY
# =========================================================

def check_donor_eligibility(user_id, donor_id=None):
    """
    Recalculate eligibility for this account's donor profiles.

    When donor_id is supplied, only that owned donor profile is evaluated.
    This is used by profile-specific actions such as availability toggling.
    """
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        if donor_id is None:
            cursor.execute(
                """
                SELECT
                    id, name, last_donation, eligible,
                    availability, health_screening_status
                FROM donors
                WHERE user_id = ?
                """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT
                    id, name, last_donation, eligible,
                    availability, health_screening_status
                FROM donors
                WHERE user_id = ? AND id = ?
                """,
                (user_id, donor_id),
            )

        for donor in cursor.fetchall():
            (
                donor_id,
                donor_name,
                last_donation,
                eligible,
                availability,
                health_status,
            ) = donor

            # Unknown or incomplete screening status is not cleared.
            if health_status != "Self-Declared Clear":
                cursor.execute(
                    """
                    UPDATE donors
                    SET eligible = 0,
                        availability = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (UNAVAILABLE, donor_id, user_id),
                )
                continue

            # No previous donation: eligible only if screening is clear.
            if not last_donation:
                if eligible != 1:
                    cursor.execute(
                        """
                        UPDATE donors
                        SET eligible = 1,
                            availability = ?
                        WHERE id = ? AND user_id = ?
                        """,
                        (AVAILABLE, donor_id, user_id),
                    )
                continue

            donation_date = parse_date(last_donation)

            if donation_date is None:
                cursor.execute(
                    """
                    UPDATE donors
                    SET eligible = 0,
                        availability = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (UNAVAILABLE, donor_id, user_id),
                )
                continue

            days_since = (get_pakistan_time().date() - donation_date).days

            if days_since < 90:
                cursor.execute(
                    """
                    UPDATE donors
                    SET eligible = 0,
                        availability = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (UNAVAILABLE, donor_id, user_id),
                )

            elif eligible != 1:
                cursor.execute(
                    """
                    UPDATE donors
                    SET eligible = 1,
                        availability = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (AVAILABLE, donor_id, user_id),
                )

                create_notification(
                    connection,
                    user_id,
                    (
                        f"{donor_name} has completed the 90-day "
                        "donation interval. Professional screening "
                        "is still required before donating."
                    ),
                    "eligibility",
                )

        connection.commit()

    except Exception:
        connection.rollback()
        app.logger.exception("Donor eligibility check failed")
        raise

    finally:
        connection.close()


# =========================================================
# 9. MATCH AND UNIT HELPERS
# =========================================================

def begin_write_transaction(connection):
    """
    Serialize critical workflows on SQLite before reading and writing.
    PostgreSQL connections already begin transactions automatically.
    """
    if not hasattr(connection, "connection"):
        connection.execute("BEGIN IMMEDIATE")


def get_reserved_units(connection, request_id, exclude_match_id=None):
    """
    Units reserved by active matches.

    These units are not counted as received units.
    They only prevent over-acceptance.
    """

    if exclude_match_id is None:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(units_pledged), 0)
            FROM request_matches
            WHERE request_id = ?
              AND status IN (?, ?, ?)
            """,
            (
                request_id,
                *ACTIVE_MATCH_STATUSES,
            ),
        ).fetchone()
    else:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(units_pledged), 0)
            FROM request_matches
            WHERE request_id = ?
              AND status IN (?, ?, ?)
              AND id != ?
            """,
            (
                request_id,
                *ACTIVE_MATCH_STATUSES,
                exclude_match_id,
            ),
        ).fetchone()

    return int(row[0] or 0)


def donor_has_active_match(connection, donor_id):
    """Return whether this specific donor profile has an active match."""
    row = connection.execute(
        """
        SELECT id
        FROM request_matches
        WHERE donor_id = ?
          AND (status IN (?, ?, ?) OR status = 'Invited')
        LIMIT 1
        """,
        (
            donor_id,
            *ACTIVE_MATCH_STATUSES,
        ),
    ).fetchone()

    return row is not None


def donor_has_other_active_match(connection, donor_id, exclude_match_id):
    """Check active matches for this donor profile, excluding its current invitation."""
    row = connection.execute(
        """
        SELECT id
        FROM request_matches
        WHERE donor_id = ?
          AND id != ?
          AND (status IN (?, ?, ?) OR status = 'Invited')
        LIMIT 1
        """,
        (donor_id, exclude_match_id, *ACTIVE_MATCH_STATUSES),
    ).fetchone()
    return row is not None


def get_active_request_count(connection, requester_user_id):
    """Count open requests that still have units outstanding."""
    row = connection.execute(
        """
        SELECT COUNT(*)
        FROM blood_requests
        WHERE user_id = ?
          AND status = 'Pending'
          AND remaining_units > 0
        """,
        (requester_user_id,),
    ).fetchone()
    return int(row[0] or 0) if row else 0


def get_latest_active_request(connection, requester_user_id):
    """Return the newest open, non-expired request for this requester."""
    now = get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S")
    row = connection.execute(
        """
        SELECT id, blood_type, location, hospital, remaining_units, needed_by
        FROM blood_requests
        WHERE user_id = ?
          AND status = 'Pending'
          AND remaining_units > 0
          AND needed_by IS NOT NULL
          AND needed_by > ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (requester_user_id, now),
    ).fetchone()
    if not row:
        return None
    return {
        "id": row[0], "blood_type": row[1], "location": row[2],
        "hospital": row[3], "remaining_units": int(row[4] or 0),
        "needed_by": row[5],
    }


def process_due_request_notifications(connection, now=None):
    """Create one-time donor reminders and overdue notifications."""
    now = now or get_pakistan_time()
    requests = connection.execute(
        """
        SELECT id, user_id, created_at, needed_by, status,
               remaining_units, overdue_notification_sent_at
        FROM blood_requests
        WHERE status NOT IN ('Cancelled', 'Fulfilled')
          AND remaining_units > 0
          AND needed_by IS NOT NULL
        """
    ).fetchall()

    for row in requests:
        request_id, requester_id, created_at, needed_by = row[:4]
        overdue_sent_at = row[6]
        deadline = parse_stored_deadline(needed_by)
        if deadline is None:
            continue

        if now >= deadline:
            if overdue_sent_at:
                continue
            create_notification(
                connection, requester_id,
                (
                    f"Blood request #{request_id} is overdue. "
                    f"{int(row[5] or 0)} unit(s) remain unfulfilled."
                ),
                "request_overdue",
                related_request_id=request_id,
            )
            active_matches = connection.execute(
                """
                SELECT id, donor_user_id
                FROM request_matches
                WHERE request_id = ?
                  AND status IN ('Accepted', 'Confirmed', 'Donation Reported')
                """,
                (request_id,),
            ).fetchall()
            for match in active_matches:
                create_notification(
                    connection, match[1],
                    (
                        f"Blood request #{request_id} has passed its deadline "
                        "and is still incomplete. Please coordinate with the requester."
                    ),
                    "request_overdue",
                    related_request_id=request_id,
                    related_match_id=match[0],
                )
            connection.execute(
                """
                UPDATE blood_requests
                SET overdue_notification_sent_at = ?
                WHERE id = ? AND overdue_notification_sent_at IS NULL
                """,
                (now.strftime("%Y-%m-%d %H:%M:%S"), request_id),
            )
            continue

        reminder_at = calculate_request_reminder_time(created_at, needed_by)
        if reminder_at is None or now < reminder_at:
            continue

        matches = connection.execute(
            """
            SELECT rm.id, rm.donor_user_id
            FROM request_matches AS rm
            WHERE rm.request_id = ?
              AND rm.status IN ('Accepted', 'Confirmed')
              AND rm.reminder_sent_at IS NULL
              AND NOT EXISTS (
                  SELECT 1 FROM donations AS d WHERE d.match_id = rm.id
              )
            """,
            (request_id,),
        ).fetchall()
        for match in matches:
            create_notification(
                connection, match[1],
                (
                    f"Donation reminder for blood request #{request_id}: "
                    f"{needed_by} is the required deadline. "
                    "Please coordinate your donation with the requester."
                ),
                "donor_reminder",
                related_request_id=request_id,
                related_match_id=match[0],
            )
            connection.execute(
                """
                UPDATE request_matches SET reminder_sent_at = ?
                WHERE id = ? AND reminder_sent_at IS NULL
                """,
                (now.strftime("%Y-%m-%d %H:%M:%S"), match[0]),
            )


def process_scheduled_notifications():
    """Entry point for the PythonAnywhere scheduled task."""
    connection = get_db_connection()
    try:
        expire_overdue_requests(connection)
        app.logger.info("Scheduled blood-request notifications processed.")
    except Exception:
        connection.rollback()
        app.logger.exception("Scheduled notification processing failed")
        raise
    finally:
        connection.close()


def expire_overdue_requests(connection):
    """
    Expire pending requests whose deadline has passed or is missing.
    Pending, unconfirmed acceptances are cancelled so donors are released.
    Confirmed matches are left intact to finish an active donation.
    """
    begin_write_transaction(connection)
    process_due_request_notifications(connection)
    now = get_current_time()

    pending_requests = connection.execute(
        """
        SELECT id, user_id, needed_by
        FROM blood_requests
        WHERE status = 'Pending'
        """
    ).fetchall()

    expired_requests = [
        row
        for row in pending_requests
        if is_request_expired(row[2])
    ]

    if not expired_requests:
        connection.commit()
        return

    for blood_request in expired_requests:
        request_id = blood_request[0]
        requester_id = blood_request[1]

        pending_matches = connection.execute(
            """
            SELECT id, donor_user_id
            FROM request_matches
            WHERE request_id = ?
              AND status IN ('Accepted', 'Invited')
              AND requester_confirmed = 0
            """,
            (request_id,),
        ).fetchall()

        connection.execute(
            """
            UPDATE blood_requests
            SET status = 'Expired',
                updated_at = ?
            WHERE id = ?
              AND status = 'Pending'
            """,
            (now, request_id),
        )

        for match in pending_matches:
            match_id = match[0]
            donor_user_id = match[1]

            connection.execute(
                """
                UPDATE request_matches
                SET status = 'Cancelled',
                    updated_at = ?
                WHERE id = ?
                  AND status IN ('Accepted', 'Invited')
                  AND requester_confirmed = 0
                """,
                (now, match_id),
            )

            create_notification(
                connection,
                donor_user_id,
                "The blood request deadline passed before confirmation. "
                "Your pending acceptance was cancelled.",
                "request_expired",
                related_request_id=request_id,
                related_match_id=match_id,
            )

        create_notification(
            connection,
            requester_id,
            "Your blood request has expired because its deadline passed "
            "or was missing. Any unconfirmed donor acceptances were cancelled.",
            "request_expired",
            related_request_id=request_id,
        )

        record_audit(
            connection,
            None,
            "request_expired",
            "blood_request",
            request_id,
            "Request expired after its deadline.",
        )

    connection.commit()


def release_unneeded_matches(
    connection,
    request_id,
    reason,
    notification_type,
    release_confirmed=False,
):
    """
    Release pending acceptances when a request closes.

    Requester-confirmed matches remain active when a requester cancels a
    request, so the agreed donation can still be completed. If the request
    becomes fully fulfilled by other donations, confirmed matches with no
    donation record are released because no units are still needed.
    """
    matches = connection.execute(
        """
        SELECT rm.id, rm.donor_user_id
        FROM request_matches AS rm
        WHERE rm.request_id = ?
          AND (
              (rm.status IN ('Accepted', 'Invited') AND rm.requester_confirmed = 0)
              OR (
                  ? = 1
                  AND rm.status = 'Confirmed'
                  AND rm.requester_confirmed = 1
              )
          )
          AND NOT EXISTS (
              SELECT 1 FROM donations AS d WHERE d.match_id = rm.id
          )
        """,
        (request_id, 1 if release_confirmed else 0),
    ).fetchall()

    for match in matches:
        match_id, donor_user_id = match[0], match[1]
        connection.execute(
            """
            UPDATE request_matches
            SET status = 'Cancelled', updated_at = ?
            WHERE id = ? AND status IN ('Accepted', 'Confirmed')
            """,
            (get_current_time(), match_id),
        )
        create_notification(
            connection, donor_user_id, reason, notification_type,
            related_request_id=request_id, related_match_id=match_id,
        )
        record_audit(
            connection, None, "match_released", "request_match", match_id, reason,
        )


def update_request_units(connection, request_id):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT requested_units, received_units, user_id, status
        FROM blood_requests
        WHERE id = ?
        """,
        (request_id,),
    )

    row = cursor.fetchone()

    if not row:
        return

    requested_units = int(row[0] or 0)
    received_units = int(row[1] or 0)
    requester_id = row[2]
    previous_status = row[3]

    remaining_units = max(requested_units - received_units, 0)

    if remaining_units == 0:
        new_status = "Fulfilled"
    elif previous_status in {"Expired", "Cancelled"}:
        new_status = previous_status
    else:
        new_status = "Pending"

    cursor.execute(
        """
        UPDATE blood_requests
        SET remaining_units = ?,
            status = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            remaining_units,
            new_status,
            get_current_time(),
            request_id,
        ),
    )

    if remaining_units == 0 and previous_status != "Fulfilled":
        create_notification(
            connection,
            requester_id,
            "Your blood request has been fully fulfilled.",
            "request_fulfilled",
            related_request_id=request_id,
        )

    if remaining_units == 0:
        release_unneeded_matches(
            connection,
            request_id,
            (
                f"Blood request #{request_id} has been fulfilled by other "
                "donation(s). Your undonated match has been released."
            ),
            "request_fulfilled",
            release_confirmed=True,
        )


# =========================================================
# 10. EMERGENCY PAGE DATA
# =========================================================
def get_emergency_page_data(user_id):
    """
    Supplies the emergency workspace sections:

    1. Create Blood Request
    2. Available Blood Requests
    3. My Blood Requests
    4. My Matches
    """

    check_donor_eligibility(user_id)

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Keep request deadlines and pending acceptances current.
        expire_overdue_requests(connection)

        # -------------------------------------------------
        # Donor profiles belonging to this user
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id, name, blood_type, location, availability,
                eligible, health_screening_status
            FROM donors
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )

        donor_profiles = cursor.fetchall()

        # -------------------------------------------------
        # Blood groups compatible with this user's donors
        # -------------------------------------------------

        compatible_groups = set()
        eligible_donor_matches = []

        for donor in donor_profiles:
            if (
                donor[4] == AVAILABLE
                and donor[5] == 1
                and donor[6] == "Self-Declared Clear"
            ):
                donor_compatible_recipients = BLOOD_COMPATIBILITY.get(
                    donor[2],
                    [],
                )
                compatible_groups.update(donor_compatible_recipients)
                eligible_donor_matches.append(
                    (donor_compatible_recipients, donor[3])
                )

        # -------------------------------------------------
        # Available blood requests
        #
        # Tuple indexes used by emergency.html:
        # 0 id
        # 1 blood_type
        # 2 urgency
        # 3 location
        # 4 hospital
        # 5 created_at
        # 6 status
        # 7 requester user_id
        # 8 requested_units
        # 9 received_units
        # 10 remaining_units
        # 11 needed_by
        # 12 reserved_units
        # 13 requester name
        # -------------------------------------------------

        available_requests_list = cursor.execute(
            """
            SELECT
                br.id,
                br.blood_type,
                br.urgency,
                br.location,
                br.hospital,
                br.created_at,
                br.status,
                br.user_id,
                br.requested_units,
                br.received_units,
                br.remaining_units,
                br.needed_by,
                COALESCE((
                    SELECT SUM(rm.units_pledged)
                    FROM request_matches AS rm
                    WHERE rm.request_id = br.id
                      AND rm.status IN (?, ?, ?)
                ), 0) AS reserved_units,
                u.name
            FROM blood_requests AS br
            LEFT JOIN users AS u ON u.id = br.user_id
            WHERE br.status = 'Pending'
              AND br.remaining_units > 0
              AND br.user_id != ?
              AND br.needed_by IS NOT NULL
              AND br.needed_by > ?
            ORDER BY
                CASE br.urgency
                    WHEN 'Emergency' THEN 1
                    ELSE 2
                END,
                br.needed_by ASC,
                br.id DESC
            """,
            (
                *ACTIVE_MATCH_STATUSES,
                user_id,
                get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ).fetchall()

        # The accept action must identify the exact donor profile, rather than
        # automatically selecting the first profile on the account.
        matching_donor_profiles_by_request = {}
        for request_row in available_requests_list:
            request_id = request_row[0]
            request_blood_type = request_row[1]
            request_location = request_row[3]
            profile_options = []
            for profile in donor_profiles:
                donor_id, donor_name = profile[0], profile[1]
                donor_blood_type, donor_location = profile[2], profile[3]
                if (
                    profile[4] == AVAILABLE
                    and profile[5] == 1
                    and profile[6] == "Self-Declared Clear"
                    and not donor_has_active_match(connection, donor_id)
                    and donor_matches_request(
                        donor_blood_type, donor_location,
                        request_blood_type, request_location,
                    )
                ):
                    profile_options.append({
                        "id": donor_id,
                        "name": donor_name,
                        "blood_type": donor_blood_type,
                    })
            matching_donor_profiles_by_request[request_id] = profile_options

        # My blood requests
        #
        # Tuple indexes:
        # 0 id, 1 blood_type, 2 urgency, 3 location,
        # 4 hospital, 5 created_at, 6 status, 7 user_id,
        # 8 requested_units, 9 received_units,
        # 10 remaining_units, 11 needed_by
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                blood_type,
                urgency,
                location,
                hospital,
                created_at,
                status,
                user_id,
                requested_units,
                received_units,
                remaining_units,
                needed_by
            FROM blood_requests
            WHERE user_id = ?
              AND status != 'Cancelled'
            ORDER BY id DESC
            """,
            (user_id,),
        )

        my_requests_list = cursor.fetchall()

        # -------------------------------------------------
        # My matches
        # Return dictionaries for emergency.html.
        # Contact information is added only after confirmation.
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                rm.id,
                rm.request_id,
                rm.donor_id,
                rm.donor_user_id,
                rm.units_pledged,
                rm.status,
                rm.requester_confirmed,
                rm.accepted_at,
                rm.confirmed_at,
                br.user_id,
                br.blood_type,
                br.location,
                br.hospital,
                br.remaining_units,
                requester.name,
                donor.name,
                br.requested_units,
                br.received_units
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            JOIN donors AS donor ON donor.id = rm.donor_id
            LEFT JOIN users AS requester ON requester.id = br.user_id
            WHERE br.user_id = ?
               OR rm.donor_user_id = ?
            ORDER BY rm.id DESC
            """,
            (user_id, user_id),
        )

        match_rows = cursor.fetchall()

        matches = []
        match_contacts = {}

        for match in match_rows:
            match_id = match[0]
            requester_id = match[9]
            donor_user_id = match[3]
            match_status = match[5]
            requester_confirmed = match[6]

            my_role = (
                "Requester"
                if requester_id == user_id
                else "Donor"
            )

            match_data = {
                "id": match_id,
                "request_id": match[1],
                "donor_id": match[2],
                "donor_user_id": donor_user_id,
                "requester_user_id": requester_id,
                "units_pledged": match[4],
                "status": (
                    "Confirmed"
                    if match_status == "Donation Reported" and my_role == "Requester"
                    else match_status
                ),
                "requester_confirmed": requester_confirmed,
                "accepted_at": match[7],
                "confirmed_at": match[8],
                "blood_type": match[10],
                "location": match[11],
                "hospital": match[12],
                "remaining_units": match[13],
                "requester_name": match[14],
                "donor_name": match[15],
                "requested_units": match[16],
                "received_units": match[17],
                "my_role": my_role,
                "requester_phone": None,
                "donor_phone": None,
            }

            # Only confirmed matches can reveal contact details.
            confirmed = (
                match_status in {
                    "Confirmed",
                    "Donation Reported",
                    "Completed",
                }
                and requester_confirmed == 1
            )

            match_data["chat_messages"] = []

            # Private chat starts once a donor has accepted the request.
            # Contact details remain hidden until requester confirmation.
            chat_available = (
                requester_confirmed == 1
                and match_status in {"Confirmed", "Donation Reported", "Completed"}
            )

            if chat_available:
                chat_rows = connection.execute(
                    """
                    SELECT
                        recent.id,
                        recent.sender_user_id,
                        recent.message,
                        recent.created_at,
                        COALESCE(sender.name, 'Network user')
                    FROM (
                        SELECT id, sender_user_id, message, created_at
                        FROM match_messages
                        WHERE match_id = ?
                        ORDER BY id DESC
                        LIMIT 100
                    ) AS recent
                    LEFT JOIN users AS sender
                        ON sender.id = recent.sender_user_id
                    ORDER BY recent.id ASC
                    """,
                    (match_id,),
                ).fetchall()

                match_data["chat_messages"] = [
                    {
                        "id": row[0],
                        "sender_user_id": row[1],
                        "message": row[2],
                        "created_at": row[3],
                        "sender_name": row[4],
                        "is_mine": row[1] == user_id,
                    }
                    for row in chat_rows
                ]

            if confirmed:
                if my_role == "Requester":
                    contact_row = connection.execute(
                        """
                        SELECT contact
                        FROM donors
                        WHERE id = ?
                          AND user_id = ?
                        """,
                        (match[2], donor_user_id),
                    ).fetchone()

                    if contact_row:
                        phone = contact_row[0]
                        match_data["donor_phone"] = phone

                        match_contacts[match_id] = {
                            "name": match[15],
                            "phone": phone,
                            "whatsapp": normalize_whatsapp_number(
                                phone
                            ),
                        }

                else:
                    contact_row = connection.execute(
                        """
                        SELECT br.contact, u.phone
                        FROM blood_requests AS br
                        LEFT JOIN users AS u ON u.id = br.user_id
                        WHERE br.id = ?
                          AND br.user_id = ?
                        """,
                        (match[1], requester_id),
                    ).fetchone()

                    if contact_row:
                        phone = contact_row[0] or contact_row[1]
                        match_data["requester_phone"] = phone

                        match_contacts[match_id] = {
                            "name": match[14],
                            "phone": phone,
                            "whatsapp": normalize_whatsapp_number(
                                phone
                            ),
                        }

            matches.append(match_data)

        # -------------------------------------------------
        # Potential matches (before a donor accepts)
        #
        # These are live suggestions only. They are not confirmed matches,
        # do not reserve units, and never expose contact details.
        # -------------------------------------------------

        potential_matches = []
        current_time = get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S")

        # Requester view: find eligible, available donors for this user's
        # open requests. A donor with any active match is not suggested.
        requester_candidates = connection.execute(
            """
            SELECT
                br.id,
                br.blood_type,
                br.urgency,
                br.location,
                br.hospital,
                br.requested_units,
                br.remaining_units,
                br.needed_by,
                d.id,
                d.user_id,
                d.name,
                d.blood_type,
                d.location
            FROM blood_requests AS br
            JOIN donors AS d
              ON d.user_id IS NOT NULL
             AND d.user_id != br.user_id
            WHERE br.user_id = ?
              AND br.status = 'Pending'
              AND br.remaining_units > 0
              AND br.needed_by IS NOT NULL
              AND br.needed_by > ?
              AND br.remaining_units > COALESCE((
                  SELECT SUM(reserved.units_pledged)
                  FROM request_matches AS reserved
                  WHERE reserved.request_id = br.id
                    AND reserved.status IN (?, ?, ?)
              ), 0)
              AND d.availability = ?
              AND d.eligible = 1
              AND d.health_screening_status = ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM request_matches AS rm
                      WHERE rm.donor_id = d.id
                    AND (rm.status IN (?, ?, ?) OR rm.status = 'Invited')
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM request_matches AS existing_match
                  WHERE existing_match.request_id = br.id
                    AND existing_match.donor_id = d.id
                    AND existing_match.status NOT IN ('Rejected', 'Cancelled')
              )
            ORDER BY br.id DESC, d.id ASC
            """,
            (
                user_id,
                current_time,
                *ACTIVE_MATCH_STATUSES,
                AVAILABLE,
                "Self-Declared Clear",
                *ACTIVE_MATCH_STATUSES,
            ),
        ).fetchall()

        seen_requester_candidates = set()

        for candidate in requester_candidates:
            (
                request_id,
                request_blood_type,
                request_urgency,
                request_location,
                request_hospital,
                requested_units,
                remaining_units,
                needed_by,
                donor_id,
                donor_user_id,
                donor_name,
                donor_blood_type,
                donor_location,
            ) = candidate

            candidate_key = (request_id, donor_user_id)

            if candidate_key in seen_requester_candidates:
                continue

            if not donor_matches_request(
                donor_blood_type,
                donor_location,
                request_blood_type,
                request_location,
            ):
                continue

            seen_requester_candidates.add(candidate_key)
            potential_matches.append({
                "kind": "potential",
                "my_role": "Requester",
                "request_id": request_id,
                "blood_type": request_blood_type,
                "urgency": request_urgency,
                "location": request_location,
                "hospital": request_hospital,
                "requested_units": requested_units,
                "remaining_units": remaining_units,
                "needed_by": needed_by,
                "candidate_name": donor_name,
                "candidate_blood_type": donor_blood_type,
                "candidate_location": donor_location,
                "status_label": "Waiting for donor acceptance",
            })

        # Donor view: show compatible open requests that this donor can
        # accept directly from My Matches. Only one card per request.
        donor_candidates = connection.execute(
            """
            SELECT
                br.id,
                br.blood_type,
                br.urgency,
                br.location,
                br.hospital,
                br.requested_units,
                br.remaining_units,
                br.needed_by,
                br.user_id,
                requester.name,
                d.id,
                d.blood_type,
                d.location
            FROM donors AS d
            JOIN blood_requests AS br
              ON br.status = 'Pending'
             AND br.remaining_units > 0
             AND br.user_id != d.user_id
            LEFT JOIN users AS requester
              ON requester.id = br.user_id
            WHERE d.user_id = ?
              AND d.availability = ?
              AND d.eligible = 1
              AND d.health_screening_status = ?
              AND br.needed_by IS NOT NULL
              AND br.needed_by > ?
              AND br.remaining_units > COALESCE((
                  SELECT SUM(reserved.units_pledged)
                  FROM request_matches AS reserved
                  WHERE reserved.request_id = br.id
                    AND reserved.status IN (?, ?, ?)
              ), 0)
              AND NOT EXISTS (
                  SELECT 1
                  FROM request_matches AS rm
                      WHERE rm.donor_id = d.id
                    AND (rm.status IN (?, ?, ?) OR rm.status = 'Invited')
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM request_matches AS existing_match
                  WHERE existing_match.request_id = br.id
                    AND existing_match.donor_id = d.id
                    AND existing_match.status NOT IN ('Rejected', 'Cancelled')
              )
            ORDER BY br.id DESC, d.id ASC
            """,
            (
                user_id,
                AVAILABLE,
                "Self-Declared Clear",
                current_time,
                *ACTIVE_MATCH_STATUSES,
                *ACTIVE_MATCH_STATUSES,
            ),
        ).fetchall()

        seen_donor_candidates = set()

        for candidate in donor_candidates:
            (
                request_id,
                request_blood_type,
                request_urgency,
                request_location,
                request_hospital,
                requested_units,
                remaining_units,
                needed_by,
                requester_id,
                requester_name,
                donor_id,
                donor_blood_type,
                donor_location,
            ) = candidate

            if request_id in seen_donor_candidates:
                continue

            if not donor_matches_request(
                donor_blood_type,
                donor_location,
                request_blood_type,
                request_location,
            ):
                continue

            seen_donor_candidates.add(request_id)
            potential_matches.append({
                "kind": "potential",
                "my_role": "Donor",
                "request_id": request_id,
                "blood_type": request_blood_type,
                "urgency": request_urgency,
                "location": request_location,
                "hospital": request_hospital,
                "requested_units": requested_units,
                "remaining_units": remaining_units,
                "needed_by": needed_by,
                "requester_name": requester_name,
                "candidate_blood_type": donor_blood_type,
                "candidate_location": donor_location,
                "status_label": "Awaiting your response",
            })

        return {
            "donor_profiles": donor_profiles,
            "available_requests": available_requests_list,
            "matching_donor_profiles_by_request": matching_donor_profiles_by_request,
            "my_requests": my_requests_list,
            "matches": matches,
            "potential_matches": potential_matches,
            "match_contacts": match_contacts,
            "health_questions": HEALTH_QUESTIONS,
        }

    finally:
        connection.close()

# =========================================================
# 11. PUBLIC LANDING PAGE
# =========================================================

@app.route("/")
def home():
    connection = get_db_connection()

    try:
        donor_count = connection.execute(
            "SELECT COUNT(*) FROM donors"
        ).fetchone()[0]
        cooldown_cutoff = (
            get_pakistan_time().date() - timedelta(days=90)
        ).isoformat()
        public_donors = connection.execute(
            """
            SELECT name, blood_type
            FROM donors
            ORDER BY name
            """
        ).fetchall()
        public_requests = connection.execute(
            """
            SELECT blood_type, location, urgency, requested_units,
                   received_units, remaining_units, needed_by
            FROM blood_requests
            WHERE status = 'Pending'
              AND remaining_units > 0
              AND needed_by IS NOT NULL
              AND needed_by > ?
            ORDER BY CASE urgency WHEN 'Emergency' THEN 1 ELSE 2 END,
                     needed_by ASC
            LIMIT 12
            """,
            (get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S"),),
        ).fetchall()
    finally:
        connection.close()

    return render_template(
        "index.html",
        donor_count=donor_count,
        public_donors=public_donors,
        public_requests=public_requests,
    )


@app.route("/explore")
def public_explore():
    """Public, contact-safe donor and blood-request exploration."""
    blood_type = clean_text(request.args.get("blood_type", "")).upper()

    if blood_type not in BLOOD_TYPES:
        flash("Please select a valid blood group.", "error")
        return redirect(url_for("home"))

    compatible_groups = get_compatible_donor_groups(blood_type)
    placeholders = ", ".join("?" for _ in compatible_groups)
    cooldown_cutoff = (
        get_pakistan_time().date() - timedelta(days=90)
    ).isoformat()
    connection = get_db_connection()

    try:
        donors = connection.execute(
            f"""
            SELECT name, blood_type, location
            FROM donors
            WHERE availability = ?
              AND eligible = 1
              AND health_screening_status = ?
              AND (last_donation IS NULL OR last_donation <= ?)
              AND blood_type IN ({placeholders})
            ORDER BY location, name
            """,
            (
                AVAILABLE,
                "Self-Declared Clear",
                cooldown_cutoff,
                *compatible_groups,
            ),
        ).fetchall()

        requests_list = connection.execute(
            """
            SELECT br.blood_type, br.location, br.urgency,
                   br.remaining_units, br.needed_by, u.name
            FROM blood_requests AS br
            LEFT JOIN users AS u ON u.id = br.user_id
            WHERE br.status = 'Pending'
              AND br.remaining_units > 0
              AND br.blood_type = ?
              AND br.needed_by IS NOT NULL
            ORDER BY br.needed_by ASC
            """,
            (blood_type,),
        ).fetchall()

        now = get_pakistan_time()
        requests_list = [
            item
            for item in requests_list
            if (
                (deadline := parse_stored_deadline(item[4])) is not None
                and deadline > now
            )
        ]
    finally:
        connection.close()

    return render_template(
        "public_explore.html",
        blood_type=blood_type,
        compatible_groups=compatible_groups,
        donors=donors,
        requests_list=requests_list,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


# =========================================================
# 13. DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = get_user_id()
    check_donor_eligibility(user_id)

    connection = get_db_connection()

    try:
        cursor = connection.cursor()
        expire_overdue_requests(connection)

        cursor.execute(
            "SELECT COUNT(*) FROM donors WHERE user_id = ?",
            (user_id,),
        )
        donor_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM blood_requests
            WHERE user_id = ? AND status = 'Pending'
            """,
            (user_id,),
        )
        active_request_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM request_matches
            WHERE donor_user_id = ?
              AND status IN ('Confirmed', 'Donation Reported')
            """,
            (user_id,),
        )
        confirmed_match_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE user_id = ? AND is_read = 0
            """,
            (user_id,),
        )
        unread_notifications = cursor.fetchone()[0]

    finally:
        connection.close()

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
        donor_count=donor_count,
        active_request_count=active_request_count,
        confirmed_match_count=confirmed_match_count,
        unread_notifications=unread_notifications,
    )


# =========================================================
# 14. DONOR REGISTRATION / PROFILE
# =========================================================

@app.route("/donor", methods=["GET", "POST"])
@login_required
def donor():

    user_id = get_user_id()
    connection = get_db_connection()

    try:
        edit_donor_id = (
            request.args.get("edit_id", type=int)
            if request.method == "GET"
            else request.form.get("donor_id", type=int)
        )
        existing_donor = None

        if edit_donor_id:
            existing_donor = connection.execute(
                """
                SELECT
                    id, name, age, contact, blood_type, location,
                    hospital, last_donation, health_screening_answers,
                    share_contact, availability
                FROM donors
                WHERE id = ? AND user_id = ?
                """,
                (edit_donor_id, user_id),
            ).fetchone()

            if not existing_donor:
                if request.method == "GET":
                    abort(404)
                flash("Donor profile not found or access denied.", "error")
                return redirect(url_for("donor"))

        if request.method == "GET":
            donor_columns = (
                "id", "name", "age", "contact", "blood_type",
                "location", "hospital", "last_donation",
                "health_screening_answers", "share_contact", "availability",
            )

            donor_form = (
                dict(zip(donor_columns, tuple(existing_donor)))
                if existing_donor
                else None
            )

            try:
                existing_screening_answers = json.loads(
                    (donor_form or {}).get("health_screening_answers") or "{}"
                )
            except (TypeError, ValueError):
                existing_screening_answers = {}

            share_contact_enabled = bool(
                (donor_form or {}).get("share_contact", 0)
            )

            return render_template(
                "donor.html",
                donor=existing_donor,
                donor_form=donor_form,
                screening_answers=existing_screening_answers,
                share_contact_enabled=share_contact_enabled,
            )

        # -------------------------------
        # Read form data
        # -------------------------------

        name = clean_text(request.form.get("name", ""))
        age_text = clean_text(request.form.get("age", ""))
        contact = clean_text(request.form.get("contact", ""))
        blood_type = clean_text(request.form.get("blood_type", ""))
        location = clean_text(request.form.get("location", ""))
        hospital = clean_text(request.form.get("hospital", ""))
        share_contact_enabled = (
            1 if request.form.get("share_contact") == "1" else 0
        )

        donated_before = request.form.get("donated_before", "no")
        last_donation = request.form.get("last_donation", "").strip()

        allowed_blood_types = {
            "O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"
        }

        # -------------------------------
        # Validate basic information
        # -------------------------------

        if not all([name, age_text, contact, blood_type, location]):
            flash("Please complete all required donor details.", "error")
            return redirect(url_for("donor"))

        try:
            age = int(age_text)
        except (TypeError, ValueError):
            flash("Please enter a valid age.", "error")
            return redirect(url_for("donor"))

        if age < 18 or age > 100:
            flash("Donors must be between 18 and 100 years old.", "error")
            return redirect(url_for("donor"))

        if blood_type not in allowed_blood_types:
            flash("Please select a valid blood group.", "error")
            return redirect(url_for("donor"))

        if not valid_phone(contact):
            flash("Please enter a valid contact number.", "error")
            return redirect(url_for("donor"))

        # -------------------------------
        # Validate donation history
        # -------------------------------

        if donated_before not in ("yes", "no"):
            flash("Please select your donation history.", "error")
            return redirect(url_for("donor"))

        if donated_before == "yes":
            if not last_donation:
                flash("Please enter your last donation date.", "error")
                return redirect(url_for("donor"))

            try:
                donation_date = date.fromisoformat(last_donation)
            except ValueError:
                flash("Please enter a valid donation date.", "error")
                return redirect(url_for("donor"))

            if donation_date > get_pakistan_time().date():
                flash("Last donation date cannot be in the future.", "error")
                return redirect(url_for("donor"))

            last_donation = donation_date.isoformat()

        else:
            last_donation = None

        # -------------------------------
        # Health screening
        # -------------------------------

        screening_fields = [
            "fever",
            "chronic_condition",
            "medication",
            "recent_surgery",
            "blood_condition"
        ]

        screening_answers = {}

        for field in screening_fields:
            answer = request.form.get(field, "").strip().lower()

            if answer not in ("yes", "no"):
                flash("Please answer every health screening question.", "error")
                return redirect(url_for("donor"))

            screening_answers[field] = answer

        consent = request.form.get("health_screening_consent")

        if consent != "confirmed":
            flash("Please confirm the health screening declaration.", "error")
            return redirect(url_for("donor"))

        # A positive answer requires professional review.
        has_positive_answer = any(
            answer == "yes"
            for answer in screening_answers.values()
        )

        if has_positive_answer:
            health_status = "Needs Professional Review"
        else:
            health_status = "Self-Declared Clear"

        # -------------------------------
        # Check 90-day donation cooldown
        # -------------------------------

        eligible = 1

        if last_donation:
            previous_date = date.fromisoformat(last_donation)
            days_since_donation = (get_pakistan_time().date() - previous_date).days

            if days_since_donation < 90:
                eligible = 0

        if health_status != "Self-Declared Clear":
            eligible = 0

        if existing_donor:
            previous_availability = (
                existing_donor["availability"]
                if hasattr(existing_donor, "keys")
                else existing_donor[10]
            )
            availability = (
                AVAILABLE
                if eligible == 1 and previous_availability == AVAILABLE
                else UNAVAILABLE
            )
        else:
            availability = AVAILABLE if eligible == 1 else UNAVAILABLE

        # -------------------------------
        # Save donor profile
        # -------------------------------

        answers_json = json.dumps(screening_answers)
        screening_date = get_pakistan_time().date().isoformat()

        if existing_donor:

            connection.execute(
                """
                UPDATE donors
                SET
                    name = ?,
                    age = ?,
                    contact = ?,
                    blood_type = ?,
                    location = ?,
                    hospital = ?,
                    last_donation = ?,
                    eligible = ?,
                    availability = ?,
                    share_contact = ?,
                    health_screening_status = ?,
                    health_screening_answers = ?,
                    health_screening_date = ?
                WHERE id = ?
                  AND user_id = ?
                """,
                (
                    name,
                    age,
                    contact,
                    blood_type,
                    location,
                    hospital,
                    last_donation,
                    eligible,
                    availability,
                    share_contact_enabled,
                    health_status,
                    answers_json,
                    screening_date,
                    existing_donor["id"] if hasattr(existing_donor, "keys") else existing_donor[0],
                    user_id
                )
            )

            message = "Your donor profile has been updated successfully."

        else:

            connection.execute(
                """
                INSERT INTO donors (
                    name,
                    age,
                    contact,
                    blood_type,
                    location,
                    hospital,
                    last_donation,
                    eligible,
                    availability,
                    user_id,
                    health_screening_status,
                    health_screening_answers,
                    health_screening_date,
                    share_contact
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    age,
                    contact,
                    blood_type,
                    location,
                    hospital,
                    last_donation,
                    eligible,
                    availability,
                    user_id,
                    health_status,
                    answers_json,
                    screening_date,
                    share_contact_enabled
                )
            )

            message = "Your donor profile has been registered successfully."

        # Notify a newly registered donor about existing open requests
        # that match their blood group and city. Profile edits do not resend alerts.
        if not existing_donor and eligible == 1 and availability == AVAILABLE:
            open_requests = connection.execute(
                """
                SELECT
                    id, user_id, blood_type, urgency, location,
                    remaining_units, needed_by
                FROM blood_requests
                WHERE status = 'Pending'
                  AND remaining_units > 0
                  AND needed_by IS NOT NULL
                ORDER BY id DESC
                """
            ).fetchall()

            now = get_pakistan_time()

            for open_request in open_requests:
                (
                    open_request_id,
                    requester_user_id,
                    request_blood_type,
                    request_urgency,
                    request_location,
                    remaining_units,
                    request_deadline_value,
                ) = open_request

                if requester_user_id == user_id:
                    continue

                request_deadline = parse_stored_deadline(
                    request_deadline_value
                )
                if request_deadline is None or request_deadline <= now:
                    continue

                if not donor_matches_request(
                    blood_type,
                    location,
                    request_blood_type,
                    request_location,
                ):
                    continue

                deadline_display = request_deadline.strftime(
                    "%d %b %Y at %I:%M %p"
                )
                create_notification(
                    connection,
                    user_id,
                    (
                        f"Match Request Found: {request_blood_type} blood "
                        f"request needs {int(remaining_units)} unit(s) in "
                        f"{request_location}. Urgency: {request_urgency}. "
                        f"Deadline: {deadline_display} (Pakistan time)."
                    ),
                    "match_request_found",
                    related_request_id=open_request_id,
                )

        if eligible == 1 and availability == AVAILABLE:
            saved_donor_id = (
                existing_donor["id"]
                if existing_donor and hasattr(existing_donor, "keys")
                else existing_donor[0]
                if existing_donor
                else get_inserted_id(connection.cursor(), connection)
            )
            if saved_donor_id:
                notify_requesters_of_compatible_donor(
                    connection,
                    saved_donor_id,
                )

        connection.commit()

        flash(message, "success")

        if health_status != "Self-Declared Clear":
            flash(
                "You are currently ineligible to donate blood.",
                "warning"
            )
        elif eligible == 0:
            flash(
                "Your profile is saved, but you are temporarily unavailable "
                "because fewer than 90 days have passed since your last donation.",
                "warning"
            )

        return redirect(url_for("dashboard"))

    except Exception:
        connection.rollback()
        app.logger.exception("Donor registration/update failed.")
        flash("Something went wrong while saving your donor profile.", "error")
        return redirect(url_for("donor"))

    finally:
        connection.close()


# =========================================================
# 15. DONOR SEARCH
# =========================================================

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    user_id = get_user_id()
    check_donor_eligibility(user_id)

    donors = []
    selected_blood_type = ""
    selected_location = ""
    compatible_donor_groups = []

    if request.method == "POST":
        selected_blood_type = form_text("blood_type", 3).upper()
        selected_location = form_text("location", 150)

        if (
            selected_blood_type not in BLOOD_TYPES
            or not selected_location
        ):
            flash("Select a valid blood group and enter a location.", "error")

        else:
            compatible_donor_groups = get_compatible_donor_groups(
                selected_blood_type
            )
            cooldown_cutoff = (
                get_pakistan_time().date() - timedelta(days=90)
            ).isoformat()

            connection = get_db_connection()

            try:
                placeholders = ", ".join(
                    "?" for _ in compatible_donor_groups
                )

                donor_rows = connection.execute(
                    f"""
                    SELECT
                        id,
                        name,
                        age,
                        contact,
                        blood_type,
                        location,
                        hospital,
                        availability,
                        eligible,
                        last_donation,
                        user_id,
                        share_contact,
                        CASE WHEN EXISTS (
                            SELECT 1
                            FROM request_matches AS rm
                            JOIN blood_requests AS br ON br.id = rm.request_id
                            WHERE rm.donor_id = donors.id
                              AND br.user_id = ?
                              AND rm.requester_confirmed = 1
                              AND rm.status IN ('Confirmed', 'Donation Reported', 'Completed')
                        ) THEN 1 ELSE 0 END AS confirmed_match
                    FROM donors
                    WHERE availability = ?
                      AND eligible = 1
                      AND health_screening_status = ?
                      AND (last_donation IS NULL OR last_donation <= ?)
                      AND blood_type IN ({placeholders})
                    ORDER BY id DESC
                    """,
                    (
                        user_id,
                        AVAILABLE,
                        "Self-Declared Clear",
                        cooldown_cutoff,
                        *compatible_donor_groups,
                    ),
                ).fetchall()

                donor_columns = (
                    "id", "name", "age", "contact", "blood_type",
                    "location", "hospital", "availability", "eligible",
                    "last_donation", "user_id", "share_contact",
                    "confirmed_match",
                )

                donors = []

                for donor_row in donor_rows:
                    donor_data = dict(zip(donor_columns, tuple(donor_row)))
                    donor_is_owner = donor_data["user_id"] == user_id
                    contact_is_shared = (
                        donor_data["share_contact"] == 1
                        and not donor_is_owner
                        and donor_data["confirmed_match"] == 1
                    )

                    if not locations_match(
                        selected_location,
                        donor_data["location"],
                    ):
                        continue

                    if not contact_is_shared:
                        donor_data["contact"] = None

                    donor_data["whatsapp"] = (
                        normalize_whatsapp_number(donor_data["contact"])
                        if donor_data["contact"]
                        else ""
                    )
                    donor_data["is_owner"] = donor_is_owner
                    donors.append(donor_data)

            except Exception:
                app.logger.exception("Donor search failed")
                flash("Unable to search donors.", "error")

            finally:
                connection.close()

    connection = get_db_connection()
    try:
        active_request = get_latest_active_request(connection, user_id)
    finally:
        connection.close()

    return render_template(
        "search.html",
        donors=donors,
        selected_blood_type=selected_blood_type,
        selected_location=selected_location,
        compatible_donor_groups=compatible_donor_groups,
        active_request=active_request,
    )


# =========================================================
# 16. DONOR DIRECTORY
# =========================================================
@app.route("/donor-list")
@login_required
def donor_list():
    check_donor_eligibility(get_user_id())
    cooldown_cutoff = (
        get_pakistan_time().date() - timedelta(days=90)
    ).isoformat()
    connection = get_db_connection()

    try:
        donors = connection.execute(
            """
            SELECT
                d.id,
                d.name,
                d.age,

                CASE
                    WHEN d.share_contact = 1
                     AND d.user_id != ?
                     AND EXISTS (
                         SELECT 1
                         FROM request_matches AS rm
                         JOIN blood_requests AS br ON br.id = rm.request_id
                         WHERE rm.donor_id = d.id
                           AND br.user_id = ?
                           AND rm.requester_confirmed = 1
                           AND rm.status IN ('Confirmed', 'Donation Reported', 'Completed')
                     )
                     AND d.availability = ?
                     AND d.eligible = 1
                     AND d.health_screening_status = ?
                     AND (d.last_donation IS NULL OR d.last_donation <= ?)
                    THEN d.contact
                    ELSE NULL
                END AS authorized_contact,

                d.blood_type,
                d.location,

                CASE
                    WHEN d.availability = ?
                     AND d.eligible = 1
                     AND d.health_screening_status = ?
                     AND (d.last_donation IS NULL OR d.last_donation <= ?)
                    THEN ?
                    ELSE ?
                END AS display_availability,

                CASE
                    WHEN d.eligible = 1
                     AND d.health_screening_status = ?
                     AND (d.last_donation IS NULL OR d.last_donation <= ?)
                    THEN 1
                    ELSE 0
                END AS display_eligible,

                d.last_donation,
                d.user_id,
                d.share_contact

            FROM donors AS d
            ORDER BY d.id DESC
            """,
            (
                get_user_id(),
                get_user_id(),
                AVAILABLE,
                "Self-Declared Clear",
                cooldown_cutoff,
                AVAILABLE,
                "Self-Declared Clear",
                cooldown_cutoff,
                AVAILABLE,
                UNAVAILABLE,
                "Self-Declared Clear",
                cooldown_cutoff,
            ),
        ).fetchall()

        donor_rows = donors
        donors = []

        for donor_row in donor_rows:
            donor_values = tuple(donor_row)
            whatsapp_number = (
                normalize_whatsapp_number(donor_values[3])
                if donor_values[3]
                else ""
            )
            donors.append(donor_values + (whatsapp_number,))

    except Exception:
        app.logger.exception("Donor directory loading failed")
        flash("Unable to load the donor directory.", "error")
        donors = []

    finally:
        connection.close()

    connection = get_db_connection()
    try:
        active_request = get_latest_active_request(connection, get_user_id())
    finally:
        connection.close()

    return render_template(
        "donor_list.html",
        donors=donors,
        active_request=active_request,
    )
    # =========================================================
# DONOR AVAILABILITY TOGGLE
# =========================================================

@app.route(
    "/toggle-availability/<int:donor_id>",
    methods=["POST"],
)
@login_required
def toggle_availability(donor_id):

    user_id = get_user_id()
    # Recalculate only the selected donor profile; sibling profiles must remain independent.
    check_donor_eligibility(user_id, donor_id=donor_id)
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT availability, eligible, health_screening_status
            FROM donors
            WHERE id = ? AND user_id = ?
            """,
            (donor_id, user_id),
        )

        donor_record = cursor.fetchone()

        if not donor_record:
            flash("Donor profile not found or access denied.", "error")
            return redirect(url_for("donor_list"))

        availability = donor_record[0]
        eligible = donor_record[1]
        health_status = donor_record[2]

        if (
            eligible != 1
            or health_status != "Self-Declared Clear"
        ):
            flash(
                "Your donor profile is not currently eligible. "
                "Availability cannot be enabled.",
                "warning",
            )
            return redirect(url_for("donor_list"))

        new_availability = (
            UNAVAILABLE
            if availability == AVAILABLE
            else AVAILABLE
        )

        cursor.execute(
            """
            UPDATE donors
            SET availability = ?
            WHERE id = ? AND user_id = ?
            """,
            (new_availability, donor_id, user_id),
        )

        if new_availability == AVAILABLE:
            notify_requesters_of_compatible_donor(connection, donor_id)

        connection.commit()

        flash(
            f"Donor availability changed to {new_availability}.",
            "success",
        )

    except Exception:
        connection.rollback()
        app.logger.exception("Availability toggle failed")
        flash("Unable to update donor availability.", "error")

    finally:
        connection.close()

    return redirect(url_for("donor_list"))

# =========================================================
# 17. EMERGENCY PAGE AND CREATE REQUEST
# =========================================================

def render_emergency_view(page_view):
    """Render one dedicated emergency workspace page with shared styling."""
    page_data = get_emergency_page_data(get_user_id())

    return render_template(
        "emergency.html",
        page_view=page_view,
        compatible_donor_groups_by_recipient={
            group: get_compatible_donor_groups(group) for group in BLOOD_TYPES
        },
        **page_data,
    )


@app.route(
    "/request",
    methods=["GET", "POST"],
    endpoint="request_blood",
)
@login_required
def blood_request():
    user_id = get_user_id()

    if request.method == "GET":
        return render_emergency_view("create")

    blood_type = form_text("blood_type", 3)
    location = form_text("location", 150)
    hospital = form_text("hospital", 150)
    contact = form_text("contact", 30)
    units_text = form_text("requested_units", 4)
    needed_by_text = (
        request.form.get("needed_by") or ""
    ).strip()

    try:
        requested_units = int(units_text)
    except (TypeError, ValueError):
        requested_units = 0

    deadline, needed_by, urgency = parse_needed_by(
        needed_by_text
    )

    if (
        blood_type not in BLOOD_TYPES
        or not location
        or not hospital
        or not valid_phone(contact)
        or not 1 <= requested_units <= 8
        or deadline is None
    ):
        flash(
            "Check the blood group, location, hospital, contact number, "
            "requested units, and future deadline.",
            "error",
        )
        return redirect(url_for("request_blood"))

    connection = get_db_connection()

    try:
        # Expire old requests before enforcing the active-request limit.
        expire_overdue_requests(connection)
        begin_write_transaction(connection)

        active_request_count = get_active_request_count(
            connection,
            user_id,
        )
        if active_request_count >= 3:
            flash(
                "You can have a maximum of 3 active blood requests. "
                "Complete or cancel an existing request before creating another.",
                "warning",
            )
            return redirect(url_for("request_blood"))

        cursor = connection.cursor()
        created_at = get_current_time()

        cursor.execute(
            """
            INSERT INTO blood_requests
                (
                    blood_type,
                    urgency,
                    location,
                    hospital,
                    contact,
                    needed_by,
                    status,
                    user_id,
                    requested_units,
                    received_units,
                    remaining_units,
                    created_at,
                    updated_at
                )
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?, ?, 0, ?, ?, ?)
            """,
            (
                blood_type,
                urgency,
                location,
                hospital,
                contact,
                needed_by,
                user_id,
                requested_units,
                requested_units,
                created_at,
                created_at,
            ),
        )

        request_id = get_inserted_id(cursor, connection)

        create_notification(
            connection,
            user_id,
            (
                f"Your {blood_type} blood request #{request_id} has been created. "
                f"Urgency: {urgency}. Blood needed by: "
                f"{deadline.strftime('%d %b %Y at %I:%M %p')} (Pakistan time)."
            ),
            "request_created",
            related_request_id=request_id,
        )

        deadline_display = deadline.strftime(
            "%d %b %Y at %I:%M %p"
        )

        # Notify only donors who can potentially fulfil this request.
        # Users without an eligible, available and cleared donor profile,
        # donors from other cities, and donors with an active match are skipped.
        cooldown_cutoff = (
            get_pakistan_time().date() - timedelta(days=90)
        ).isoformat()

        donor_notification_candidates = cursor.execute(
            """
            SELECT d.user_id, d.blood_type, d.location, d.name
            FROM donors AS d
            WHERE d.user_id IS NOT NULL
              AND d.user_id != ?
              AND d.availability = ?
              AND d.eligible = 1
              AND d.health_screening_status = ?
              AND (d.last_donation IS NULL OR d.last_donation <= ?)
              AND NOT EXISTS (
                  SELECT 1
                  FROM request_matches AS rm
                      WHERE rm.donor_id = d.id
                    AND (rm.status IN (?, ?, ?) OR rm.status = 'Invited')
              )
            ORDER BY d.user_id, d.id
            """,
            (
                user_id,
                AVAILABLE,
                "Self-Declared Clear",
                cooldown_cutoff,
                *ACTIVE_MATCH_STATUSES,
            ),
        ).fetchall()

        notification_recipient_ids = get_notification_recipient_user_ids(
            donor_notification_candidates,
            blood_type,
            location,
            excluded_user_id=user_id,
        )

        compatible_profile_labels = {}
        for donor_row in donor_notification_candidates:
            donor_user_id, donor_blood_type, donor_location, donor_name = donor_row
            if donor_matches_request(
                donor_blood_type, donor_location, blood_type, location
            ):
                compatible_profile_labels.setdefault(donor_user_id, [])
                label = f"{donor_name} ({donor_blood_type})"
                if label not in compatible_profile_labels[donor_user_id]:
                    compatible_profile_labels[donor_user_id].append(label)

        for recipient_user_id in notification_recipient_ids:
            profile_text = ", ".join(
                compatible_profile_labels.get(recipient_user_id, [])
            )
            notification_message = (
                f"New {urgency.lower()} blood request: "
                f"{blood_type}, {requested_units} unit(s), "
                f"location: {location}. "
                f"Blood needed by: {deadline_display} (Pakistan time). "
                f"Compatible donor profile(s): {profile_text}."
            )
            create_notification(
                connection,
                recipient_user_id,
                notification_message,
                "blood_request",
                related_request_id=request_id,
            )

        available_donor_ids = cursor.execute(
            """
            SELECT id
            FROM donors
            WHERE availability = ?
              AND eligible = 1
              AND health_screening_status = ?
            """,
            (AVAILABLE, "Self-Declared Clear"),
        ).fetchall()
        for donor_row in available_donor_ids:
            notify_requesters_of_compatible_donor(
                connection,
                donor_row[0],
            )

        record_audit(
            connection,
            user_id,
            "blood_request_created",
            "blood_request",
            request_id,
            (
                f"Requested {requested_units} units of {blood_type}. "
                f"Urgency: {urgency}. Deadline: {needed_by}."
            ),
        )

        connection.commit()

        flash(
            f"Blood request created successfully. "
            f"Urgency: {urgency}.",
            "success",
        )

    except Exception:
        connection.rollback()
        app.logger.exception("Blood request creation failed")
        flash("Unable to create the blood request.", "error")

    finally:
        connection.close()

    return redirect(url_for("request_blood"))

# =========================================================
# 18. EMERGENCY WORKSPACE PAGES
# Each navigation item opens its own page view while sharing the same UI.
# =========================================================

@app.route("/available-requests")
@login_required
def available_requests():
    return render_emergency_view("find")


@app.route("/my-requests")
@login_required
def my_requests():
    return render_emergency_view("my_requests")


@app.route(
    "/cancel-request/<int:request_id>",
    methods=["POST"],
)
@login_required
def cancel_blood_request(request_id):
    """Allow only the request owner to close their own open request."""
    user_id = get_user_id()
    connection = get_db_connection()

    try:
        begin_write_transaction(connection)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id, status
            FROM blood_requests
            WHERE id = ?
            """,
            (request_id,),
        )
        blood_request = cursor.fetchone()

        if not blood_request:
            flash("Blood request not found.", "error")
            return redirect(url_for("my_requests"))

        requester_id = blood_request[0]
        request_status = blood_request[1]

        if requester_id != user_id:
            flash("You can only cancel your own blood requests.", "error")
            return redirect(url_for("my_requests"))

        if request_status != "Pending":
            flash(
                "Only an open request can be cancelled. "
                "Its current status is " + str(request_status) + ".",
                "warning",
            )
            return redirect(url_for("my_requests"))

        now = get_current_time()

        cursor.execute(
            """
            UPDATE blood_requests
            SET status = 'Cancelled',
                updated_at = ?
            WHERE id = ?
              AND user_id = ?
              AND status = 'Pending'
            """,
            (now, request_id, user_id),
        )

        release_unneeded_matches(
            connection,
            request_id,
            (
                f"Blood request #{request_id} was cancelled by the requester. "
                "Your undonated match has been released."
            ),
            "request_cancelled",
        )

        reported_matches = cursor.execute(
            """
            SELECT id, donor_user_id
            FROM request_matches
            WHERE request_id = ? AND status = 'Donation Reported'
            """,
            (request_id,),
        ).fetchall()

        for match in reported_matches:
            create_notification(
                connection,
                match[1],
                (
                    f"The requester cancelled the remaining open units for "
                    f"blood request #{request_id}. Your reported donation "
                    "remains active for receipt confirmation."
                ),
                "request_cancelled",
                related_request_id=request_id,
                related_match_id=match[0],
            )

        connection.execute(
            """
            DELETE FROM notifications
            WHERE related_request_id = ?
              AND user_id = ?
            """,
            (request_id, requester_id),
        )

        record_audit(
            connection,
            user_id,
            "blood_request_cancelled",
            "blood_request",
            request_id,
            (
                "Requester cancelled the open request. Received units and "
                "donation records were preserved; pending unconfirmed "
                "acceptances were released."
            ),
        )

        connection.commit()
        flash(
            "Your blood request was cancelled. Received units and donation "
            "history were preserved, and pending donor acceptances were released.",
            "success",
        )

    except Exception:
        connection.rollback()
        app.logger.exception("Blood request cancellation failed")
        flash("Unable to cancel this blood request right now.", "error")

    finally:
        connection.close()

    return redirect(url_for("my_requests"))


@app.route("/my-matches")
@login_required
def my_matches():
    return render_emergency_view("my_matches")


# 19. ACCEPT A REQUEST
# =========================================================
@app.route(
    "/accept-request/<int:request_id>",
    methods=["POST"],
)
@login_required
def accept_request(request_id):
    user_id = get_user_id()

    try:
        units_pledged = int(request.form.get("units_pledged") or "1")
        selected_donor_id = int(request.form.get("donor_id") or "0")
    except (ValueError, TypeError):
        units_pledged = 0
        selected_donor_id = 0

    if not 1 <= units_pledged <= 8:
        flash("Enter a valid number of units.")
        return redirect(url_for("available_requests"))

    if selected_donor_id <= 0:
        flash("Select the donor profile you want to use for this match.", "warning")
        return redirect(url_for("available_requests"))

    check_donor_eligibility(user_id, donor_id=selected_donor_id)
    connection = get_db_connection()
    match_id = None

    try:
        expire_overdue_requests(connection)
        begin_write_transaction(connection)
        cursor = connection.cursor()
        matching_donor = cursor.execute(
            """
            SELECT id, blood_type, location, eligible, availability,
                   health_screening_status, last_donation
            FROM donors
            WHERE user_id = ? AND id = ?
            """,
            (user_id, selected_donor_id),
        ).fetchone()

        if not matching_donor:
            flash("The selected donor profile does not belong to your account.", "error")
            return redirect(url_for("available_requests"))

        cursor.execute(
            """
            SELECT
                id,
                blood_type,
                location,
                user_id,
                remaining_units,
                status,
                needed_by
            FROM blood_requests
            WHERE id = ?
            """,
            (request_id,),
        )

        blood_request = cursor.fetchone()

        if not blood_request:
            flash("This request no longer exists.")
            return redirect(url_for("available_requests"))

        request_blood_type = blood_request[1]
        request_location = blood_request[2]
        requester_id = blood_request[3]
        remaining_units = int(blood_request[4] or 0)
        request_status = blood_request[5]
        needed_by = blood_request[6]

        if requester_id == user_id:
            flash("You cannot accept your own blood request.")
            return redirect(url_for("available_requests"))

        if request_status != "Pending" or remaining_units <= 0:
            flash("This request is no longer available.")
            return redirect(url_for("available_requests"))

        if is_request_expired(needed_by):
            flash(
                "This request has expired because its required deadline "
                "has passed. It can no longer be accepted."
            )
            return redirect(url_for("available_requests"))

        reserved_units = get_reserved_units(
            connection,
            request_id,
        )

        available_units = max(
            remaining_units - reserved_units,
            0,
        )

        if units_pledged > available_units:
            flash(
                f"Only {available_units} unreserved units are available "
                "for acceptance."
            )
            return redirect(url_for("available_requests"))

        donor_id = matching_donor[0]
        donor_type = matching_donor[1]
        donor_location = matching_donor[2]
        donor_eligible = matching_donor[3]
        donor_availability = matching_donor[4]
        screening_status = matching_donor[5]
        last_donation = matching_donor[6]
        cooldown_cutoff = (
            get_pakistan_time().date() - timedelta(days=90)
        ).isoformat()

        if (
            donor_has_active_match(connection, donor_id)
            or request_blood_type not in BLOOD_COMPATIBILITY.get(donor_type, [])
            or not locations_match(donor_location, request_location)
            or donor_eligible != 1
            or donor_availability != AVAILABLE
            or screening_status != "Self-Declared Clear"
            or (last_donation and str(last_donation) > cooldown_cutoff)
        ):
            flash(
                "The selected donor profile is unavailable, ineligible, "
                "already matched, or incompatible with this request.",
                "warning",
            )
            return redirect(url_for("available_requests"))

        cursor.execute(
            """
            SELECT id, status
            FROM request_matches
            WHERE request_id = ? AND donor_id = ?
            """,
            (request_id, donor_id),
        )

        old_match = cursor.fetchone()

        if old_match:
            old_match_id = old_match[0]
            old_status = old_match[1]

            if old_status not in {"Rejected", "Cancelled"}:
                flash("You have already processed this donor/request match.")
                return redirect(url_for("available_requests"))

            cursor.execute(
                """
                UPDATE request_matches
                SET donor_user_id = ?,
                    units_pledged = ?,
                    status = 'Confirmed',
                    requester_confirmed = 1,
                    accepted_at = ?,
                    confirmed_at = ?,
                    completed_at = NULL,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    user_id,
                    units_pledged,
                    get_current_time(),
                    get_current_time(),
                    get_current_time(),
                    old_match_id,
                ),
            )

            match_id = old_match_id

        else:
            cursor.execute(
                """
                INSERT INTO request_matches
                    (
                        request_id,
                        donor_id,
                        donor_user_id,
                        units_pledged,
                        status,
                        requester_confirmed,
                        accepted_at,
                        confirmed_at,
                        updated_at
                    )
                VALUES (?, ?, ?, ?, 'Confirmed', 1, ?, ?, ?)
                """,
                (
                    request_id,
                    donor_id,
                    user_id,
                    units_pledged,
                    get_current_time(),
                    get_current_time(),
                    get_current_time(),
                ),
            )

            match_id = get_inserted_id(cursor, connection)

        create_notification(
            connection,
            requester_id,
            "A donor accepted your blood request. Your match is active and private chat is ready.",
            "match_acceptance",
            related_request_id=request_id,
            related_match_id=match_id,
        )

        create_notification(
            connection,
            user_id,
            "You accepted the blood request. Your match is active and private chat is ready.",
            "match_confirmed",
            related_request_id=request_id,
            related_match_id=match_id,
        )

        record_audit(
            connection,
            user_id,
            "request_accepted",
            "request_match",
            match_id,
            f"Accepted request {request_id}.",
        )

        connection.commit()
        flash(
            "Request accepted. Your match is active. Open My Matches to coordinate the donation.",
            "success",
        )

    except Exception:
        connection.rollback()
        app.logger.exception("Request acceptance failed")
        flash("Unable to accept this request.")

    finally:
        connection.close()

    if match_id:
        return redirect(
            url_for("my_matches") + f"#match-chat-{match_id}"
        )

    return redirect(url_for("available_requests"))

# =========================================================
# 20. DONOR CANCELS PENDING ACCEPTANCE
# =========================================================

@app.route("/request-donor/<int:donor_id>", methods=["POST"])
@login_required
def request_donor(donor_id):
    """Send an invitation using the requester's newest active blood request."""
    user_id = get_user_id()
    connection = get_db_connection()
    try:
        expire_overdue_requests(connection)
        begin_write_transaction(connection)
        blood_request = get_latest_active_request(connection, user_id)
        if not blood_request:
            flash("Create an active blood request before requesting a donor.", "warning")
            return redirect(request.referrer or url_for("donor_list"))

        donor = connection.execute(
            """
            SELECT id, user_id, blood_type, location, availability,
                   eligible, health_screening_status, last_donation
            FROM donors WHERE id = ?
            """,
            (donor_id,),
        ).fetchone()
        if not donor or not donor[1] or donor[1] == user_id:
            flash("This donor profile is unavailable.", "error")
            return redirect(request.referrer or url_for("donor_list"))
        donor_user_id = donor[1]
        if donor_has_active_match(connection, donor_id):
            flash("This donor profile already has an active match or invitation.", "warning")
            return redirect(request.referrer or url_for("donor_list"))
        if (
            donor[4] != AVAILABLE or donor[5] != 1
            or donor[6] != "Self-Declared Clear"
            or (
                donor[7]
                and str(donor[7]) > (
                    get_pakistan_time().date() - timedelta(days=90)
                ).isoformat()
            )
            or not donor_matches_request(
                donor[2], donor[3], blood_request["blood_type"], blood_request["location"]
            )
        ):
            flash("This donor is no longer eligible or compatible with your active request.", "warning")
            return redirect(request.referrer or url_for("donor_list"))

        reserved_units = get_reserved_units(connection, blood_request["id"])
        if reserved_units >= blood_request["remaining_units"]:
            flash("All units for your active request are already matched.", "warning")
            return redirect(request.referrer or url_for("donor_list"))

        old = connection.execute(
            "SELECT id, status FROM request_matches WHERE request_id = ? AND donor_id = ?",
            (blood_request["id"], donor_id),
        ).fetchone()
        if old and old[1] not in {"Rejected", "Cancelled"}:
            flash("You have already requested this donor for this blood request.", "warning")
            return redirect(request.referrer or url_for("donor_list"))

        now = get_current_time()
        if old:
            match_id = old[0]
            connection.execute(
                """
                UPDATE request_matches
                SET donor_user_id = ?, units_pledged = 1,
                    status = 'Confirmed', requester_confirmed = 1,
                    accepted_at = ?, confirmed_at = ?,
                    completed_at = NULL, updated_at = ?
                WHERE id = ?
                """,
                (donor_user_id, now, now, now, match_id),
            )
        else:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO request_matches
                    (request_id, donor_id, donor_user_id, units_pledged,
                     status, requester_confirmed, accepted_at, confirmed_at, updated_at)
                VALUES (?, ?, ?, 1, 'Confirmed', 1, ?, ?, ?)
                """,
                (blood_request["id"], donor_id, donor_user_id, now, now, now),
            )
            match_id = get_inserted_id(cursor, connection)

        create_notification(
            connection, donor_user_id,
            f"You have been matched for a {blood_request['blood_type']} blood request "
            f"in {blood_request['location']}. Open My Matches to coordinate the donation.",
            "match_confirmed", related_request_id=blood_request["id"],
            related_match_id=match_id,
        )
        create_notification(
            connection, user_id,
            f"Your request was matched with donor {donor_id}. The match is active and private chat is ready.",
            "match_confirmed", related_request_id=blood_request["id"],
            related_match_id=match_id,
        )
        record_audit(connection, user_id, "match_confirmed", "request_match", match_id,
                     f"Requester started a match with donor profile {donor_id} for request {blood_request['id']}.")
        connection.commit()
        flash("Donor requested successfully. Your match is now active.", "success")
    except Exception:
        connection.rollback()
        app.logger.exception("Donor invitation failed")
        flash("Unable to send a donor request right now.", "error")
    finally:
        connection.close()
    return redirect(request.referrer or url_for("donor_list"))


@app.route("/accept-match-invitation/<int:match_id>", methods=["POST"])
@login_required
def accept_match_invitation(match_id):
    user_id = get_user_id()
    check_donor_eligibility(user_id)
    connection = get_db_connection()
    try:
        expire_overdue_requests(connection)
        begin_write_transaction(connection)
        row = connection.execute(
            """
            SELECT rm.request_id, rm.donor_id, rm.donor_user_id, rm.status,
                   br.user_id, br.remaining_units, br.status, br.needed_by
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ?
            """,
            (match_id,),
        ).fetchone()
        if not row:
            flash("Donor invitation not found.", "error")
            return redirect(url_for("my_matches"))
        request_id, donor_id, donor_user_id, status, requester_id, remaining, request_status, needed_by = row
        if donor_user_id != user_id or status != "Invited":
            flash("This invitation is no longer available to you.", "warning")
            return redirect(url_for("my_matches"))
        donor_profile = connection.execute(
            """
            SELECT availability, eligible, health_screening_status, last_donation
            FROM donors
            WHERE id = ? AND user_id = ?
            """,
            (donor_id, user_id),
        ).fetchone()
        cooldown_cutoff = (
            get_pakistan_time().date() - timedelta(days=90)
        ).isoformat()
        if (
            not donor_profile
            or donor_profile[0] != AVAILABLE
            or donor_profile[1] != 1
            or donor_profile[2] != "Self-Declared Clear"
            or (
                donor_profile[3]
                and str(donor_profile[3]) > cooldown_cutoff
            )
        ):
            flash("Your donor profile is not currently eligible to accept this invitation.", "warning")
            return redirect(url_for("my_matches"))
        if request_status != "Pending" or int(remaining or 0) < 1 or is_request_expired(needed_by):
            connection.execute(
                "UPDATE request_matches SET status = 'Cancelled', updated_at = ? WHERE id = ? AND status = 'Invited'",
                (get_current_time(), match_id),
            )
            connection.commit()
            flash("The blood request has expired or is already fulfilled.", "warning")
            return redirect(url_for("my_matches"))
        # The account may own several donor profiles. Only this donor_id
        # is restricted to one active match at a time.
        if donor_has_other_active_match(connection, donor_id, match_id):
            flash("You already have another active match. Complete it before accepting this invitation.", "warning")
            return redirect(url_for("my_matches"))
        reserved = get_reserved_units(connection, request_id, exclude_match_id=match_id)
        if 1 > max(int(remaining or 0) - reserved, 0):
            flash("No unreserved units remain for this request.", "warning")
            return redirect(url_for("my_matches"))
        now = get_current_time()
        connection.execute(
            """
            UPDATE request_matches
            SET status = 'Confirmed', requester_confirmed = 1,
                confirmed_at = ?, updated_at = ?
            WHERE id = ? AND status = 'Invited'
            """,
            (now, now, match_id),
        )
        create_notification(connection, requester_id,
            "The donor accepted your invitation. Your match is now active and private chat is ready.",
            "match_confirmed", related_request_id=request_id, related_match_id=match_id)
        create_notification(connection, user_id,
            "You accepted the request. Your match is now active and private chat is ready.",
            "match_confirmed", related_request_id=request_id, related_match_id=match_id)
        record_audit(connection, user_id, "match_confirmed", "request_match", match_id,
                     "Donor accepted the requester's invitation.")
        connection.commit()
        flash("Invitation accepted. Your match is now active.", "success")
    except Exception:
        connection.rollback()
        app.logger.exception("Donor invitation acceptance failed")
        flash("Unable to accept this invitation.", "error")
    finally:
        connection.close()
    return redirect(url_for("my_matches") + f"#match-chat-{match_id}")


@app.route(
    "/cancel-acceptance/<int:match_id>",
    methods=["POST"],
)
@login_required
def cancel_acceptance(match_id):
    user_id = get_user_id()
    connection = get_db_connection()

    try:
        begin_write_transaction(connection)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                rm.request_id,
                rm.donor_user_id,
                rm.status,
                rm.requester_confirmed,
                br.user_id
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ?
            """,
            (match_id,),
        )

        match = cursor.fetchone()

        if not match:
            flash("Match not found.")
            return redirect(url_for("my_matches"))

        request_id = match[0]
        donor_user_id = match[1]
        match_status = match[2]
        requester_confirmed = match[3]
        requester_id = match[4]

        if donor_user_id != user_id:
            flash("Only the matched donor can cancel this acceptance.")
            return redirect(url_for("my_matches"))

        if match_status != "Accepted" or requester_confirmed == 1:
            flash("Only a pending, unconfirmed acceptance can be cancelled.")
            return redirect(url_for("my_matches"))

        cursor.execute(
            """
            UPDATE request_matches
            SET status = 'Cancelled',
                updated_at = ?
            WHERE id = ?
            """,
            (get_current_time(), match_id),
        )

        create_notification(
            connection,
            requester_id,
            "A donor cancelled their pending acceptance.",
            "match_cancelled",
            related_request_id=request_id,
            related_match_id=match_id,
        )

        record_audit(
            connection,
            user_id,
            "match_cancelled",
            "request_match",
            match_id,
            "Donor cancelled pending acceptance.",
        )

        connection.commit()
        flash("Your pending acceptance has been cancelled.")

    except Exception:
        connection.rollback()
        app.logger.exception("Acceptance cancellation failed")
        flash("Unable to cancel this acceptance.")

    finally:
        connection.close()

    return redirect(url_for("my_matches"))


# =========================================================
# 21. REQUESTER CONFIRMS OR REJECTS MATCH
# =========================================================

@app.route(
    "/confirm-match/<int:match_id>",
    methods=["POST"],
)
@login_required
def confirm_match(match_id):
    user_id = get_user_id()

    action = (
        request.form.get("action") or "confirm"
    ).strip().lower()

    if action not in {"confirm", "reject"}:
        flash("Invalid match action.")
        return redirect(url_for("my_matches"))

    connection = get_db_connection()

    try:
        begin_write_transaction(connection)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                rm.id,
                rm.request_id,
                rm.donor_user_id,
                rm.status,
                rm.requester_confirmed,
                br.user_id,
                br.remaining_units,
                rm.units_pledged,
                br.needed_by,
                br.status
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ?
            """,
            (match_id,),
        )

        match = cursor.fetchone()

        if not match:
            flash("Match not found.")
            return redirect(url_for("my_matches"))

        request_id = match[1]
        donor_user_id = match[2]
        match_status = match[3]
        requester_confirmed = match[4]
        requester_id = match[5]
        remaining_units = int(match[6] or 0)
        units_pledged = int(match[7] or 0)
        needed_by = match[8]
        request_status = match[9]

        if requester_id != user_id:
            flash("Only the requester can process this match.")
            return redirect(url_for("my_matches"))

        if match_status != "Accepted" or requester_confirmed:
            flash("This match has already been processed.")
            return redirect(url_for("my_matches"))

        if action == "reject":
            cursor.execute(
                """
                UPDATE request_matches
                SET status = 'Rejected',
                    updated_at = ?
                WHERE id = ?
                """,
                (get_current_time(), match_id),
            )

            create_notification(
                connection,
                donor_user_id,
                "The requester rejected your acceptance.",
                "match_rejected",
                related_request_id=request_id,
                related_match_id=match_id,
            )

            flash("Match acceptance rejected.")

        else:
            if request_status != "Pending" or is_request_expired(needed_by):
                now = get_current_time()

                cursor.execute(
                    """
                    UPDATE request_matches
                    SET status = 'Cancelled',
                        updated_at = ?
                    WHERE id = ?
                      AND status = 'Accepted'
                      AND requester_confirmed = 0
                    """,
                    (now, match_id),
                )

                create_notification(
                    connection,
                    donor_user_id,
                    "The request is no longer open or its deadline passed. "
                    "Your pending acceptance was cancelled.",
                    "request_expired",
                    related_request_id=request_id,
                    related_match_id=match_id,
                )

                record_audit(
                    connection,
                    user_id,
                    "request_expired",
                    "request_match",
                    match_id,
                    "Pending match cancelled because the request was closed or expired.",
                )

                connection.commit()
                flash(
                    "This request is no longer open or its deadline has passed. "
                    "The pending acceptance was cancelled and the donor is now free "
                    "to accept another request.",
                    "warning",
                )
                return redirect(url_for("my_matches"))

            reserved_units = get_reserved_units(
                connection,
                request_id,
                exclude_match_id=match_id,
            )

            available_units = max(
                remaining_units - reserved_units,
                0,
            )

            if units_pledged > available_units:
                flash(
                    "The remaining unreserved units have changed. "
                    "This match cannot be confirmed."
                )
                return redirect(url_for("my_matches"))

            cursor.execute(
                """
                UPDATE request_matches
                SET status = 'Confirmed',
                    requester_confirmed = 1,
                    confirmed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    get_current_time(),
                    get_current_time(),
                    match_id,
                ),
            )

            create_notification(
                connection,
                donor_user_id,
                (
                    "The requester confirmed your match. "
                    "You can now coordinate the donation."
                ),
                "match_confirmed",
                related_request_id=request_id,
                related_match_id=match_id,
            )

            create_notification(
                connection,
                requester_id,
                "You confirmed a donor match for your request.",
                "match_confirmed",
                related_request_id=request_id,
                related_match_id=match_id,
            )

            flash("Match confirmed successfully.")

        record_audit(
            connection,
            user_id,
            f"match_{action}",
            "request_match",
            match_id,
            f"Requester processed match {match_id}.",
        )

        connection.commit()

    except Exception:
        connection.rollback()
        app.logger.exception("Match confirmation failed")
        flash("Unable to process the match.")

    finally:
        connection.close()

    return redirect(url_for("my_matches"))


# =========================================================
# 22. MATCH DETAILS
# =========================================================

@app.route("/match/<int:match_id>")
@login_required
def match_detail(match_id):
    user_id = get_user_id()
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                rm.id,
                rm.request_id,
                rm.donor_id,
                rm.donor_user_id,
                rm.units_pledged,
                rm.status,
                rm.requester_confirmed,
                rm.accepted_at,
                rm.confirmed_at,
                br.user_id,
                br.blood_type,
                br.location,
                br.hospital,
                CASE
                    WHEN rm.requester_confirmed = 1
                     AND rm.status IN ('Confirmed', 'Donation Reported', 'Completed')
                    THEN br.contact
                    ELSE NULL
                END AS requester_contact,
                br.remaining_units,
                donor.name,
                CASE
                    WHEN rm.requester_confirmed = 1
                     AND rm.status IN ('Confirmed', 'Donation Reported')
                    THEN donor.contact
                    ELSE NULL
                END AS donor_contact,
                donor.blood_type,
                donor.location,
                requester.name,
                CASE
                    WHEN rm.requester_confirmed = 1
                     AND rm.status IN ('Confirmed', 'Donation Reported')
                    THEN requester.phone
                    ELSE NULL
                END AS requester_phone
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            JOIN donors AS donor ON donor.id = rm.donor_id
            LEFT JOIN users AS requester ON requester.id = br.user_id
            WHERE rm.id = ?
              AND (
                    br.user_id = ?
                    OR rm.donor_user_id = ?
              )
            """,
            (match_id, user_id, user_id),
        )

        match = cursor.fetchone()

        if not match:
            abort(404)

        confirmed = (
            match[5] in {"Confirmed", "Donation Reported", "Completed"}
            and match[6] == 1
        )

        contact_details = None

        if confirmed:
            if match[9] == user_id:
                phone = match[16]

                contact_details = {
                    "name": match[15],
                    "phone": phone,
                    "whatsapp": normalize_whatsapp_number(phone),
                }

            elif match[3] == user_id:
                phone = match[13] or match[20]

                contact_details = {
                    "name": match[19],
                    "phone": phone,
                    "whatsapp": normalize_whatsapp_number(phone),
                }

    finally:
        connection.close()

    return render_template(
        "match_detail.html",
        match=match,
        contact_details=contact_details,
    )


# =========================================================
# 23. MATCH CHAT
# =========================================================

@app.route("/match/<int:match_id>/messages", methods=["GET"])
@login_required
def get_match_messages(match_id):
    user_id = get_user_id()
    try:
        after_id = max(int(request.args.get("after", 0)), 0)
    except (TypeError, ValueError):
        after_id = 0
    connection = get_db_connection()
    try:
        match = connection.execute(
            """
            SELECT rm.status, br.user_id, rm.donor_user_id,
                   rm.requester_confirmed
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ? AND (br.user_id = ? OR rm.donor_user_id = ?)
            """,
            (match_id, user_id, user_id),
        ).fetchone()
        if (
            not match
            or match[3] != 1
            or match[0] not in {"Confirmed", "Donation Reported", "Completed"}
        ):
            return jsonify({"ok": False, "messages": []}), 403
        rows = connection.execute(
            """
            SELECT mm.id, mm.message, mm.created_at, mm.sender_user_id,
                   COALESCE(u.name, 'Network user')
            FROM match_messages AS mm
            LEFT JOIN users AS u ON u.id = mm.sender_user_id
            WHERE mm.match_id = ? AND mm.id > ?
            ORDER BY mm.id ASC LIMIT 100
            """,
            (match_id, after_id),
        ).fetchall()
        return jsonify({
            "ok": True,
            "messages": [
                {"id": row[0], "message": row[1], "created_at": row[2],
                 "sender_user_id": row[3], "sender_name": row[4],
                 "is_mine": row[3] == user_id}
                for row in rows
            ],
        })
    finally:
        connection.close()


@app.route(
    "/send-match-message/<int:match_id>",
    methods=["POST"],
)
@login_required
def send_match_message(match_id):
    user_id = get_user_id()
    message_text = form_text("message", 2000)
    if not message_text:
        if request.headers.get("Accept") == "application/json":
            return jsonify({"ok": False, "error": "Write a message before sending."}), 400
        flash("Write a message before sending.", "error")
        return redirect(url_for("my_matches") + f"#match-chat-{match_id}")

    connection = get_db_connection()
    saved_message = None
    try:
        begin_write_transaction(connection)
        match = connection.execute(
            """
            SELECT rm.request_id, rm.donor_user_id, rm.status,
                   rm.requester_confirmed, br.user_id
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ?
              AND (br.user_id = ? OR rm.donor_user_id = ?)
            """,
            (match_id, user_id, user_id),
        ).fetchone()
        if not match:
            if request.headers.get("Accept") == "application/json":
                return jsonify({"ok": False, "error": "This match is unavailable."}), 403
            flash("This match is unavailable or you do not have access.", "error")
            return redirect(url_for("my_matches"))
        if (
            match[2] not in {"Confirmed", "Donation Reported", "Completed"}
            or match[3] != 1
        ):
            if request.headers.get("Accept") == "application/json":
                return jsonify({"ok": False, "error": "Chat is not available for this match."}), 403
            flash("Chat is available only while this match is active.", "warning")
            return redirect(url_for("my_matches") + f"#match-chat-{match_id}")

        requester_id = match[4]
        recipient_id = match[1] if user_id == requester_id else requester_id
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO match_messages (match_id, sender_user_id, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (match_id, user_id, message_text, get_current_time()),
        )
        message_id = get_inserted_id(cursor, connection)
        saved_message = {
            "id": message_id,
            "message": message_text,
            "created_at": get_current_time(),
            "sender_name": session.get("user_name", "You"),
            "sender_user_id": user_id,
            "is_mine": True,
        }
        create_notification(
            connection, recipient_id,
            "You have a new private message in your blood request match.",
            "match_message", related_request_id=match[0], related_match_id=match_id,
        )
        record_audit(connection, user_id, "match_message_sent", "request_match",
                     match_id, "A private message was sent in the match chat.")
        connection.commit()
    except Exception:
        connection.rollback()
        app.logger.exception("Match chat message could not be sent")
        if request.headers.get("Accept") == "application/json":
            return jsonify({"ok": False, "error": "Unable to send your message."}), 500
        flash("Unable to send your message. Please try again.", "error")
    finally:
        connection.close()

    if request.headers.get("Accept") == "application/json":
        return jsonify({"ok": True, "message": saved_message})
    return redirect(url_for("my_matches") + f"#match-chat-{match_id}")


# =========================================================
# 24. REPORT DONATION
# =========================================================

@app.route(
    "/report-match-donation/<int:match_id>",
    methods=["POST"],
)
@login_required
def report_match_donation(match_id):
    """Requester records the donation actually received; donor gets a profile copy."""
    user_id = get_user_id()
    try:
        units = int(request.form.get("units") or "1")
    except (ValueError, TypeError):
        units = 0
    parsed_date = parse_date((request.form.get("donation_date") or "").strip())
    if not 1 <= units <= 8 or parsed_date is None or parsed_date > get_pakistan_time().date():
        flash("Enter a valid donation date and number of units.", "error")
        return redirect(url_for("my_matches"))

    connection = get_db_connection()
    try:
        begin_write_transaction(connection)
        match = connection.execute(
            """
            SELECT rm.request_id, rm.donor_id, rm.donor_user_id,
                   rm.units_pledged, rm.status, rm.requester_confirmed,
                   br.remaining_units, br.user_id, br.hospital, br.location
            FROM request_matches AS rm
            JOIN blood_requests AS br ON br.id = rm.request_id
            WHERE rm.id = ?
            """,
            (match_id,),
        ).fetchone()
        if not match:
            flash("Match not found.", "error")
            return redirect(url_for("my_matches"))
        request_id, donor_id, donor_user_id, pledged, status, confirmed, remaining, requester_id, hospital, location = match
        if requester_id != user_id:
            flash("Only the requester can report the donation received.", "error")
            return redirect(url_for("my_matches"))
        if status not in {"Confirmed", "Donation Reported"} or confirmed != 1:
            flash("Only an active confirmed match can have a donation report.", "warning")
            return redirect(url_for("my_matches"))
        if units > int(pledged or 0) or units > int(remaining or 0):
            flash("Reported units exceed the pledged or remaining units.", "error")
            return redirect(url_for("my_matches"))

        existing_donation = connection.execute(
            """
            SELECT id, status, requester_confirmed
            FROM donations
            WHERE match_id = ?
            """,
            (match_id,),
        ).fetchone()

        if existing_donation and (
            existing_donation[1] == "Confirmed"
            or existing_donation[2] == 1
        ):
            flash("A completed donation report already exists for this match.", "warning")
            return redirect(url_for("my_matches"))

        cursor = connection.cursor()
        now = get_current_time()

        if existing_donation:
            # Finalize a legacy donor-reported row with the requester's actual receipt.
            donation_id = existing_donation[0]
            cursor.execute(
                """
                UPDATE donations
                SET donation_date = ?,
                    hospital = ?,
                    location = ?,
                    units = ?,
                    status = 'Confirmed',
                    requester_confirmed = 1,
                    confirmed_at = ?
                WHERE id = ?
                """,
                (
                    parsed_date.isoformat(),
                    hospital,
                    location,
                    units,
                    now,
                    donation_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO donations
                    (donor_id, donation_date, hospital, location,
                     request_id, match_id, units, status, requester_confirmed, confirmed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed', 1, ?)
                """,
                (donor_id, parsed_date.isoformat(), hospital, location,
                 request_id, match_id, units, now),
            )
            donation_id = get_inserted_id(cursor, connection)
        connection.execute(
            "UPDATE request_matches SET status = 'Completed', completed_at = ?, updated_at = ? WHERE id = ?",
            (now, now, match_id),
        )
        connection.execute(
            "UPDATE blood_requests SET received_units = received_units + ? WHERE id = ?",
            (units, request_id),
        )
        connection.execute(
            """
            UPDATE donors
            SET last_donation = ?, eligible = 0, availability = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                get_pakistan_time().date().isoformat(),
                UNAVAILABLE,
                donor_id,
                donor_user_id,
            ),
        )
        update_request_units(connection, request_id)
        create_notification(connection, donor_user_id,
            f"The requester recorded receipt of {units} unit(s). A copy is saved in your donation history.",
            "donation_reported_by_requester", related_request_id=request_id, related_match_id=match_id)
        create_notification(connection, requester_id,
            f"You recorded receipt of {units} unit(s) from your donor. The match is complete.",
            "donation_reported_by_requester", related_request_id=request_id, related_match_id=match_id)
        record_audit(connection, user_id, "donation_reported_by_requester", "donation", donation_id,
                     f"Requester recorded {units} received unit(s) for match {match_id}.")
        connection.commit()
        flash("Donation recorded. A copy is now saved in the donor's profile history.", "success")
    except Exception:
        connection.rollback()
        app.logger.exception("Requester donation report failed")
        flash("Unable to record this donation right now.", "error")
    finally:
        connection.close()
    return redirect(url_for("my_matches"))


# =========================================================
# 24. REQUESTER CONFIRMS RECEIPT
# =========================================================

@app.route(
    "/confirm-receipt/<int:donation_id>",
    methods=["POST"],
)
@login_required
def confirm_receipt(donation_id):
    user_id = get_user_id()

    try:
        received_units = int(
            request.form.get("received_units") or "0"
        )
    except (ValueError, TypeError):
        received_units = 0

    if not 1 <= received_units <= 8:
        flash("Enter the actual number of units received.")
        return redirect(url_for("my_matches"))

    connection = get_db_connection()

    try:
        begin_write_transaction(connection)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                d.id,
                d.request_id,
                d.match_id,
                d.donor_id,
                d.units,
                d.status,
                d.requester_confirmed,
                d.donation_date,
                br.user_id,
                br.remaining_units,
                rm.donor_user_id,
                rm.status
            FROM donations AS d
            JOIN blood_requests AS br ON br.id = d.request_id
            JOIN request_matches AS rm ON rm.id = d.match_id
            WHERE d.id = ?
            """,
            (donation_id,),
        )

        donation = cursor.fetchone()

        if not donation:
            flash("Donation record not found.")
            return redirect(url_for("my_matches"))

        request_id = donation[1]
        match_id = donation[2]
        donor_id = donation[3]
        reported_units = int(donation[4] or 0)
        donation_status = donation[5]
        already_confirmed = donation[6]
        donation_date = donation[7]
        requester_id = donation[8]
        remaining_units = int(donation[9] or 0)
        donor_user_id = donation[10]
        match_status = donation[11]

        if requester_id != user_id:
            flash("Only the requester can confirm receipt.")
            return redirect(url_for("my_matches"))

        if already_confirmed or donation_status == "Confirmed":
            flash("This donation has already been confirmed.")
            return redirect(url_for("my_matches"))

        if match_status != "Donation Reported":
            flash("This match is not awaiting receipt confirmation.")
            return redirect(url_for("my_matches"))

        if received_units > reported_units:
            flash("You cannot confirm more units than the donor reported.")
            return redirect(url_for("my_matches"))

        if received_units > remaining_units:
            flash(f"Only {remaining_units} units remain on this request.")
            return redirect(url_for("my_matches"))

        if received_units <= 0:
            flash("The confirmed quantity must be greater than zero.")
            return redirect(url_for("my_matches"))

        cursor.execute(
            """
            UPDATE donations
            SET units = ?,
                status = 'Confirmed',
                requester_confirmed = 1,
                confirmed_at = ?
            WHERE id = ?
            """,
            (
                received_units,
                get_current_time(),
                donation_id,
            ),
        )

        cursor.execute(
            """
            UPDATE request_matches
            SET status = 'Completed',
                completed_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                get_current_time(),
                get_current_time(),
                match_id,
            ),
        )

        cursor.execute(
            """
            UPDATE blood_requests
            SET received_units = received_units + ?
            WHERE id = ?
            """,
            (received_units, request_id),
        )

        # Start donor cooldown only after receipt confirmation.
        confirmed_donation_date = get_pakistan_time().date().isoformat()

        cursor.execute(
            """
            UPDATE donors
            SET last_donation = ?,
                eligible = 0,
                availability = ?
            WHERE id = ?
            """,
            (
                confirmed_donation_date,
                UNAVAILABLE,
                donor_id,
            ),
        )
        update_request_units(connection, request_id)

        create_notification(
            connection,
            donor_user_id,
            f"The requester confirmed receipt of {received_units} unit(s).",
            "receipt_confirmed",
            related_request_id=request_id,
            related_match_id=match_id,
        )

        create_notification(
            connection,
            requester_id,
            "You confirmed the received donation.",
            "receipt_confirmed",
            related_request_id=request_id,
            related_match_id=match_id,
        )

        record_audit(
            connection,
            user_id,
            "receipt_confirmed",
            "donation",
            donation_id,
            f"Confirmed receipt of {received_units} units.",
        )

        connection.commit()
        flash("Receipt confirmed. Request units have been updated.")

    except Exception:
        connection.rollback()
        app.logger.exception("Receipt confirmation failed")
        flash("Unable to confirm receipt.")

    finally:
        connection.close()

    return redirect(url_for("my_matches"))


# =========================================================
# 25. DONATION HISTORY
# =========================================================

@app.route("/donation-history")
@login_required
def donation_history():
    user_id = get_user_id()

    connection = get_db_connection()

    try:
        donations = connection.execute(
            """
            SELECT
                d.id,
                d.donation_date,
                d.hospital,
                d.location,
                d.units,
                d.status,
                d.requester_confirmed,
                d.request_id,
                d.match_id,
                donor.name,
                donor.blood_type,
                rm.donor_user_id,
                br.user_id
            FROM donations AS d
            JOIN donors AS donor ON donor.id = d.donor_id
            LEFT JOIN request_matches AS rm ON rm.id = d.match_id
            LEFT JOIN blood_requests AS br ON br.id = d.request_id
            WHERE donor.user_id = ?
               OR br.user_id = ?
            ORDER BY d.id DESC
            """,
            (user_id, user_id),
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "donation_history.html",
        donations=donations,
    )


# =========================================================
# 26. NOTIFICATIONS
# =========================================================

@app.route("/notifications")
@login_required
def notifications():
    user_id = get_user_id()
    connection = get_db_connection()

    notification_labels = {
        "blood_request": "New blood request",
        "match_request_found": "Match request found",
        "request_created": "Your blood request was created",
        "match_acceptance": "Donor accepted your request",
        "match_waiting": "Your acceptance is waiting",
        "match_confirmed": "Match confirmed",
        "match_message": "Private chat message",
        "match_rejected": "Match rejected",
        "match_cancelled": "Donor cancelled acceptance",
        "request_cancelled": "Blood request cancelled",
        "request_expired": "Blood request expired",
        "request_fulfilled": "Blood request fulfilled",
        "donation_reported": "Donation reported",
        "receipt_confirmed": "Donation receipt confirmed",
        "eligibility": "Donor eligibility update",
    }

    notifications_view = []

    try:
        notifications_list = connection.execute(
            """
            SELECT
                id, message, notification_type, created_at,
                is_read, related_request_id, related_match_id
            FROM notifications
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

        for row in notifications_list:
            notification_id = row[0]
            notification_type = row[2]
            request_id = row[5]
            match_id = row[6]

            if match_id:
                target_url = url_for("my_matches")
                if notification_type == "match_message":
                    target_url += f"#match-chat-{match_id}"
            elif notification_type in ("blood_request", "match_request_found"):
                target_url = url_for("available_requests")
            elif request_id:
                target_url = url_for("my_requests")
            elif notification_type == "eligibility":
                target_url = url_for("donor")
            else:
                target_url = url_for("dashboard")

            notifications_view.append({
                "id": notification_id,
                "message": row[1],
                "type": notification_type,
                "label": notification_labels.get(
                    notification_type,
                    (notification_type or "update").replace("_", " ").title(),
                ),
                "created_at": row[3],
                "is_read": bool(row[4]),
                "request_id": request_id,
                "match_id": match_id,
                "target_url": target_url,
            })

        unread_count = sum(
            1 for notification in notifications_view
            if not notification["is_read"]
        )

    finally:
        connection.close()

    return render_template(
        "notifications.html",
        notifications=notifications_view,
        unread_count=unread_count,
        total_notifications=len(notifications_view),
    )


@app.route("/notifications/unread-count")
@login_required
def unread_notification_count():
    count = get_unread_notification_count(get_user_id())

    return app.response_class(
        json.dumps({"unread_count": count}),
        mimetype="application/json",
    )


@app.route("/notifications/updates")
@login_required
def notification_updates():
    user_id = get_user_id()
    try:
        after_id = max(int(request.args.get("after_id", 0)), 0)
    except (TypeError, ValueError):
        after_id = 0

    connection = get_db_connection()
    try:
        rows = connection.execute(
            """
            SELECT id, message, notification_type, created_at,
                   related_request_id, related_match_id
            FROM notifications
            WHERE user_id = ? AND id > ?
            ORDER BY id ASC
            LIMIT 50
            """,
            (user_id, after_id),
        ).fetchall()
        unread_count = get_unread_notification_count(user_id)
        total_count = connection.execute(
            "SELECT COUNT(*) FROM notifications WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]

        labels = {
            "blood_request": "New blood request",
            "match_request_found": "Match request found",
            "request_created": "Your blood request was created",
            "match_acceptance": "Donor accepted your request",
            "match_waiting": "Your acceptance is waiting",
            "match_confirmed": "Match confirmed",
            "match_message": "Private chat message",
            "match_rejected": "Match rejected",
            "match_cancelled": "Donor cancelled acceptance",
            "request_cancelled": "Blood request cancelled",
            "request_expired": "Blood request expired",
            "request_fulfilled": "Blood request fulfilled",
            "donation_reported": "Donation reported",
            "receipt_confirmed": "Donation receipt confirmed",
            "eligibility": "Donor eligibility update",
        }
        notifications_data = []
        for row in rows:
            notification_id, message, kind, created_at, request_id, match_id = row
            if match_id:
                target_url = url_for("my_matches")
                if kind == "match_message":
                    target_url += f"#match-chat-{match_id}"
            elif kind in ("blood_request", "match_request_found"):
                target_url = url_for("available_requests")
            elif request_id:
                target_url = url_for("my_requests")
            elif kind == "eligibility":
                target_url = url_for("donor")
            else:
                target_url = url_for("dashboard")
            notifications_data.append({
                "id": notification_id,
                "message": message,
                "type": kind,
                "label": labels.get(kind, (kind or "update").replace("_", " ").title()),
                "created_at": created_at,
                "request_id": request_id,
                "match_id": match_id,
                "target_url": target_url,
            })

        return jsonify({
            "ok": True,
            "unread_count": unread_count,
            "total_count": total_count,
            "notifications": notifications_data,
        })
    finally:
        connection.close()


@app.route(
    "/notification/open/<int:notification_id>",
    methods=["POST"],
)
@login_required
def open_notification(notification_id):
    user_id = get_user_id()
    connection = get_db_connection()
    try:
        notification = connection.execute(
            """
            SELECT notification_type, related_request_id, related_match_id
            FROM notifications
            WHERE id = ? AND user_id = ?
            """,
            (notification_id, user_id),
        ).fetchone()
        if not notification:
            abort(404)

        connection.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
            (notification_id, user_id),
        )
        connection.commit()

        kind, request_id, match_id = notification
        if match_id:
            target_url = url_for("my_matches")
            if kind == "match_message":
                target_url += f"#match-chat-{match_id}"
        elif kind in ("blood_request", "match_request_found"):
            target_url = url_for("available_requests")
        elif request_id:
            target_url = url_for("my_requests")
        elif kind == "eligibility":
            target_url = url_for("donor")
        else:
            target_url = url_for("dashboard")
        return redirect(target_url)
    except Exception:
        connection.rollback()
        app.logger.exception("Notification could not be opened")
        flash("Unable to open this notification.", "error")
        return redirect(url_for("notifications"))
    finally:
        connection.close()


@app.route(
    "/notification/read/<int:notification_id>",
    methods=["POST"],
)
@login_required
def mark_notification_read(notification_id):
    connection = get_db_connection()

    try:
        connection.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE id = ? AND user_id = ?
            """,
            (notification_id, get_user_id()),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        app.logger.exception("Notification update failed")
        flash("Unable to update notification.")

    finally:
        connection.close()

    return redirect(url_for("notifications"))

# =========================================================
# 27. PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = get_user_id()
    connection = get_db_connection()

    # -----------------------------------------
    # UPDATE PROFILE
    # -----------------------------------------
    if request.method == "POST":
        name = form_text("name", 100)

        email = (
            request.form.get("email") or ""
        ).strip().lower()

        phone = (
            request.form.get("phone") or ""
        ).strip()

        cnic = normalize_cnic(
            request.form.get("cnic") or ""
        )

        language_preference = (
            request.form.get("language_preference") or "English"
        ).strip()

        if (
            language_preference not in {"Sindhi", "Urdu", "English"}
            or not name
            or (email and not valid_email(email))
            or (phone and not valid_phone(phone))
            or not cnic
            or not (email or phone)
        ):
            connection.close()
            flash("Check your name, CNIC, email, and phone number.")
            return redirect(url_for("profile"))

        try:
            connection.execute(
                """
                UPDATE users
                SET name = ?, email = ?, phone = ?, cnic = ?,
                    language_preference = ?
                WHERE id = ?
                """,
                (
                    name, email or None, phone or None, cnic,
                    language_preference, user_id,
                ),
            )

            connection.commit()
            session["user_name"] = name
            flash("Profile updated successfully.", "success")

        except Exception:
            connection.rollback()
            app.logger.exception("Profile update failed")
            flash(
                "Unable to update profile. The CNIC, email, or phone "
                "may already be registered.",
                "error",
            )

        finally:
            connection.close()

        return redirect(url_for("profile"))

    # -----------------------------------------
    # LOAD PROFILE AND PERSONAL HISTORY
    # -----------------------------------------
    try:
        cursor = connection.cursor()

        # Account information: only the logged-in user.
        cursor.execute(
            """
            SELECT id, name, email, phone, cnic, language_preference
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )
        user = cursor.fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        # Load every donor profile independently for the profile page.
        cursor.execute(
            """
            SELECT
                id, name, age, blood_type, location,
                availability, eligible, last_donation,
                health_screening_status
            FROM donors
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )
        donor_profiles = cursor.fetchall()

        # Count only donations confirmed by the requester.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM donations AS d
            JOIN donors AS donor ON donor.id = d.donor_id
            WHERE donor.user_id = ?
              AND d.status = 'Confirmed'
              AND d.requester_confirmed = 1
            """,
            (user_id,),
        )
        donation_count = cursor.fetchone()[0]

        # Every blood request created by this user.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM blood_requests
            WHERE user_id = ?
              AND status = 'Fulfilled'
            """,
            (user_id,),
        )
        request_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM blood_requests
            WHERE user_id = ?
              AND status = 'Pending'
              AND remaining_units > 0
            """,
            (user_id,),
        )
        active_request_count = cursor.fetchone()[0]

        # This user's complete donation history, including donations
        # made through any donor profile and donations received as requester.
        cursor.execute(
            """
            SELECT
                d.id,
                d.donation_date,
                d.hospital,
                d.location,
                d.units,
                d.status,
                d.requester_confirmed,
                d.request_id,
                donor.id,
                donor.name,
                donor.blood_type,
                donor.user_id,
                br.user_id
            FROM donations AS d
            LEFT JOIN donors AS donor ON donor.id = d.donor_id
            LEFT JOIN blood_requests AS br ON br.id = d.request_id
            WHERE (donor.user_id = ? OR br.user_id = ?)
              AND d.status = 'Confirmed'
              AND d.requester_confirmed = 1
            ORDER BY d.id DESC
            """,
            (user_id, user_id),
        )
        donations = cursor.fetchall()

        # This user's complete blood-request history.
        cursor.execute(
            """
            SELECT
                id,
                blood_type,
                urgency,
                location,
                hospital,
                requested_units,
                received_units,
                remaining_units,
                status,
                created_at
            FROM blood_requests
            WHERE user_id = ?
              AND status != 'Cancelled'
            ORDER BY id DESC
            """,
            (user_id,),
        )
        my_requests = cursor.fetchall()

    except Exception:
        app.logger.exception("Profile data loading failed")
        flash("Unable to load your profile.", "error")
        return redirect(url_for("dashboard"))

    finally:
        connection.close()

    return render_template(
        "profile.html",
        user=user,
        donor_profiles=donor_profiles,
        donation_count=donation_count,
        request_count=request_count,
        active_request_count=active_request_count,
        donations=donations,
        my_requests=my_requests,
    )

# =========================================================
# 28. SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    name = form_text("name", 100)

    email = (
        request.form.get("email") or ""
    ).strip().lower()

    phone = (
        request.form.get("phone") or ""
    ).strip()

    cnic = normalize_cnic(
        request.form.get("cnic") or ""
    )

    password = request.form.get("password") or ""

    if not name:
        flash("Please enter your name.")
        return redirect(url_for("signup"))

    if not email and not phone:
        flash("Enter an email address or phone number.")
        return redirect(url_for("signup"))

    if email and not valid_email(email):
        flash("Enter a valid email address.")
        return redirect(url_for("signup"))

    if phone and not valid_phone(phone):
        flash("Enter a valid phone number.")
        return redirect(url_for("signup"))

    if not cnic:
        flash("Enter a valid 13-digit CNIC number.")
        return redirect(url_for("signup"))

    if len(password) < 8 or len(password) > 128:
        flash("Password must be between 8 and 128 characters.")
        return redirect(url_for("signup"))

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE cnic = ?
               OR (? IS NOT NULL AND lower(email) = lower(?))
               OR (? IS NOT NULL AND phone = ?)
            LIMIT 1
            """,
            (
                cnic,
                email or None,
                email or None,
                phone or None,
                phone or None,
            ),
        )

        if cursor.fetchone():
            flash(
                "An account already exists with this CNIC, email, "
                "or phone number."
            )
            return redirect(url_for("signup"))

        cursor.execute(
            """
            INSERT INTO users (name, email, phone, password, cnic)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email or None,
                phone or None,
                generate_password_hash(password),
                cnic,
            ),
        )

        connection.commit()
        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    except Exception:
        connection.rollback()
        app.logger.exception("Signup failed")
        flash("Unable to create account. Please check your information.")

    finally:
        connection.close()

    return redirect(url_for("signup"))


# =========================================================
# 29. LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    login_input = (
        request.form.get("login_input") or ""
    ).strip()

    password = request.form.get("password") or ""

    if not login_input or not password:
        flash(
            "Enter your email/phone and password.",
            "error",
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT id, name, password
            FROM users
            WHERE lower(email) = ? OR phone = ?
            """,
            (login_input.lower(), login_input),
        ).fetchone()

    except Exception:
        app.logger.exception("Login account lookup failed")
        flash(
            "Unable to sign in right now. Please try again.",
            "error",
        )
        return redirect(url_for("login"))

    finally:
        connection.close()

    if not user:
        flash(
            "Invalid user name.",
            "error",
        )
        return redirect(url_for("login"))

    if not check_password_hash(user[2], password):
        flash("Invalid password.", "error")
        return redirect(url_for("login"))

    session.clear()
    session["user_id"] = user[0]
    session["user_name"] = user[1]
    session.permanent = True
    session["_csrf_token"] = secrets.token_urlsafe(32)

    flash("Login successful.", "success")
    return redirect(url_for("dashboard"))


# =========================================================
# 30. LOGOUT
# =========================================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))


# =========================================================
# 31. LEGACY FULFIL ROUTE
# =========================================================

@app.route(
    "/fulfill/<int:request_id>",
    methods=["POST"],
)
@login_required
def fulfill_request(request_id):
    flash(
        "Requests are fulfilled automatically after the requester "
        "confirms the received donation."
    )

    return redirect(url_for("request_blood"))


# =========================================================
# 32. ERROR HANDLERS
# =========================================================

@app.errorhandler(400)
def bad_request(error):
    return (
        "Bad request. A required security token may be missing "
        "or invalid. Please refresh the page and try again.",
        400,
    )


@app.errorhandler(403)
def forbidden(error):
    return "You are not authorized to perform this action.", 403


@app.errorhandler(404)
def not_found(error):
    return "The requested page or record was not found.", 404


@app.errorhandler(413)
def request_too_large(error):
    return "Submitted request is too large.", 413


# =========================================================
# 33. INITIALIZE DATABASE
# =========================================================

init_database()


if __name__ == "__main__":
    app.run()
