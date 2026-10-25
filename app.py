
import os
import re
import hmac
import secrets
import logging

from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    abort,
    url_for,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database import get_db_connection, init_database


# =========================================================
# 1. FLASK CONFIGURATION AND SESSION SECURITY
# =========================================================

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"

secret_key = os.getenv("SECRET_KEY")

if IS_PRODUCTION and not secret_key:
    raise RuntimeError(
        "Set the SECRET_KEY environment variable before "
        "running the application in production."
    )

app.config.update(
    SECRET_KEY=secret_key or secrets.token_hex(32),
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
    "O-", "O+", "A-", "A+",
    "B-", "B+", "AB-", "AB+",
}

URGENCY_LEVELS = {
    "Normal", "Urgent", "Emergency",
}

AVAILABLE = "Available"
UNAVAILABLE = "Not Available"

# Donor blood type -> compatible recipient blood types.
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


# =========================================================
# 3. INPUT VALIDATION
# =========================================================

def clean_text(value, max_length=150):
    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value or len(value) > max_length:
        return None

    if any(ord(char) < 32 for char in value):
        return None

    return value


def valid_phone(value):
    return bool(
        value
        and re.fullmatch(r"\+?[0-9 ()-]{7,20}", value)
        and sum(char.isdigit() for char in value) >= 7
    )


def valid_email(value):
    return bool(
        value
        and len(value) <= 254
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value)
    )


def parse_date(value):
    if not value:
        return None

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

    if parsed > date.today():
        return None

    return parsed


def form_text(name, max_length=150):
    return clean_text(request.form.get(name), max_length)


# =========================================================
# 4. AUTHENTICATION
# =========================================================

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


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": get_csrf_token}


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
# 7. NOTIFICATION HELPER
# =========================================================

def create_notification(
    connection,
    user_id,
    message,
    notification_type,
):
    if not user_id:
        return

    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO notifications
            (user_id, message, notification_type, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            message,
            notification_type,
            created_at,
        ),
    )


# =========================================================
# 8. 90-DAY DONOR ELIGIBILITY
# =========================================================

def check_donor_eligibility(user_id):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, last_donation, eligible
            FROM donors
            WHERE user_id = ?
            """,
            (user_id,),
        )

        donors = cursor.fetchall()

        for donor_record in donors:
            donor_id = donor_record[0]
            donor_name = donor_record[1]
            last_donation = donor_record[2]
            eligible = donor_record[3]

            if not last_donation:
                continue

            donation_date = parse_date(last_donation)

            if donation_date is None:
                continue

            days_since_donation = (
                date.today() - donation_date
            ).days

            if days_since_donation >= 90 and eligible == 0:
                cursor.execute(
                    """
                    UPDATE donors
                    SET eligible = 1
                    WHERE id = ? AND user_id = ?
                    """,
                    (donor_id, user_id),
                )

                create_notification(
                    connection,
                    user_id,
                    (
                        f"{donor_name} has completed "
                        "the 90-day donation interval."
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
# 9. PUBLIC HOME PAGE
# =========================================================

@app.route("/")
def home():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Never return donor contact numbers to the public homepage.
        cursor.execute(
            """
            SELECT name, blood_type, location
            FROM donors
            WHERE availability = ?
              AND eligible = 1
            ORDER BY id DESC
            LIMIT 20
            """,
            (AVAILABLE,),
        )

        public_donors = cursor.fetchall()

        # Request contact information is excluded from public results.
        cursor.execute(
            """
            SELECT
                br.id,
                u.name,
                br.blood_type,
                br.urgency,
                br.location,
                br.hospital,
                br.status
            FROM blood_requests AS br
            LEFT JOIN users AS u ON br.user_id = u.id
            WHERE br.status = 'Pending'
            ORDER BY br.id DESC
            LIMIT 20
            """
        )

        public_requests = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "index.html",
        donors=public_donors,
        requests=public_requests,
    )


# =========================================================
# 10. DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    check_donor_eligibility(session["user_id"])

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
    )


# =========================================================
# 11. DONOR REGISTRATION
# =========================================================

@app.route("/donor", methods=["GET", "POST"])
@login_required
def donor():
    if request.method == "GET":
        return render_template("donor.html")

    name = form_text("name", 100)
    age_text = form_text("age", 3)
    contact = form_text("contact", 30)
    blood_type = form_text("blood_type", 3)
    location = form_text("location", 150)

    last_donation = (
        request.form.get("last_donation") or ""
    ).strip()

    if not all([name, age_text, contact, blood_type, location]):
        flash("Please complete all required donor fields.")
        return redirect(url_for("donor"))

    try:
        age = int(age_text)
    except ValueError:
        age = 0

    if not 18 <= age <= 100:
        flash("Donor age must be between 18 and 100.")
        return redirect(url_for("donor"))

    if not valid_phone(contact):
        flash("Please enter a valid donor contact number.")
        return redirect(url_for("donor"))

    if blood_type not in BLOOD_TYPES:
        flash("Please select a valid blood group.")
        return redirect(url_for("donor"))

    if last_donation:
        donation_date = parse_date(last_donation)

        if donation_date is None:
            flash("Invalid donation date or date is in the future.")
            return redirect(url_for("donor"))

        eligible = int(
            (date.today() - donation_date).days >= 90
        )

        availability = AVAILABLE if eligible else UNAVAILABLE

    else:
        last_donation = None
        eligible = 1
        availability = AVAILABLE

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Prevent duplicate contact records for the same account.
        cursor.execute(
            """
            SELECT id
            FROM donors
            WHERE user_id = ? AND contact = ?
            """,
            (session["user_id"], contact),
        )

        if cursor.fetchone():
            flash("You have already registered this contact as a donor.")
            return redirect(url_for("donor"))

        cursor.execute(
            """
            INSERT INTO donors
                (
                    name,
                    age,
                    contact,
                    blood_type,
                    location,
                    availability,
                    last_donation,
                    eligible,
                    user_id
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                age,
                contact,
                blood_type,
                location,
                availability,
                last_donation,
                eligible,
                session["user_id"],
            ),
        )

        connection.commit()
        flash("Donor registered successfully.")

    except Exception:
        connection.rollback()
        app.logger.exception("Donor registration failed")
        flash("Unable to register donor. Please check your information.")

    finally:
        connection.close()

    return redirect(url_for("donor"))


# =========================================================
# 12. DONOR LIST
# =========================================================

@app.route("/donor-list")
@login_required
def donor_list():
    user_id = session["user_id"]

    check_donor_eligibility(user_id)

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Column order:
        # 0 id, 1 name, 2 age, 3 contact, 4 blood_type,
        # 5 location, 6 availability, 7 eligible, 8 owner user_id.
        # Contact is returned only for the record's owner.
        cursor.execute(
            """
            SELECT
                id,
                name,
                age,
                CASE WHEN user_id = ? THEN contact ELSE NULL END,
                blood_type,
                location,
                availability,
                eligible,
                user_id
            FROM donors
            ORDER BY id DESC
            """,
            (user_id,),
        )

        donors = cursor.fetchall()

    finally:
        connection.close()

    return render_template("donor_list.html", donors=donors)


# =========================================================
# 13. REPORT DONATION — OWNER ONLY
# =========================================================

@app.route(
    "/report-donation/<int:donor_id>",
    methods=["GET", "POST"],
)
@login_required
def report_donation(donor_id):
    user_id = session["user_id"]
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, blood_type
            FROM donors
            WHERE id = ? AND user_id = ?
            """,
            (donor_id, user_id),
        )

        donor_record = cursor.fetchone()

        if not donor_record:
            flash("You are not authorized to manage this donor.")
            return redirect(url_for("donor_list"))

        if request.method == "GET":
            return render_template(
                "report_donation.html",
                donor=donor_record,
                today=date.today().isoformat(),
            )

        donation_date_text = form_text("donation_date", 10)
        hospital = form_text("hospital", 150)
        location = form_text("location", 150)

        parsed_date = parse_date(donation_date_text)

        if (
            not all([hospital, location])
            or parsed_date is None
        ):
            flash("Enter a valid donation date, hospital, and location.")
            return redirect(
                url_for("report_donation", donor_id=donor_id)
            )

        cursor.execute(
            """
            INSERT INTO donations
                (donor_id, donation_date, hospital, location)
            VALUES (?, ?, ?, ?)
            """,
            (
                donor_id,
                parsed_date.isoformat(),
                hospital,
                location,
            ),
        )

        # A new donation starts a new 90-day interval.
        cursor.execute(
            """
            UPDATE donors
            SET last_donation = ?,
                eligible = 0,
                availability = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                parsed_date.isoformat(),
                UNAVAILABLE,
                donor_id,
                user_id,
            ),
        )

        connection.commit()
        flash("Donation reported successfully.")

    except Exception:
        connection.rollback()
        app.logger.exception("Donation report failed")
        flash("Unable to save the donation report.")

    finally:
        connection.close()

    return redirect(url_for("donor_list"))


# =========================================================
# 14. TOGGLE AVAILABILITY — OWNER ONLY
# =========================================================

@app.route(
    "/toggle-availability/<int:donor_id>",
    methods=["POST"],
)
@login_required
def toggle_availability(donor_id):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT availability, eligible
            FROM donors
            WHERE id = ? AND user_id = ?
            """,
            (donor_id, session["user_id"]),
        )

        donor_record = cursor.fetchone()

        if not donor_record:
            flash("You are not authorized to modify this donor.")
            return redirect(url_for("donor_list"))

        current_status = donor_record[0]
        eligible = donor_record[1]

        if current_status == AVAILABLE:
            new_status = UNAVAILABLE

        elif eligible:
            new_status = AVAILABLE

        else:
            flash("This donor has not completed the 90-day interval.")
            return redirect(url_for("donor_list"))

        cursor.execute(
            """
            UPDATE donors
            SET availability = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                new_status,
                donor_id,
                session["user_id"],
            ),
        )

        connection.commit()
        flash("Donor availability updated.")

    except Exception:
        connection.rollback()
        app.logger.exception("Availability update failed")
        flash("Unable to update donor availability.")

    finally:
        connection.close()

    return redirect(url_for("donor_list"))


# =========================================================
# 15. SEARCH DONORS
# =========================================================

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    donors = []

    if request.method == "POST":
        blood_type = form_text("blood_type", 3)
        location = form_text("location", 150)

        if blood_type not in BLOOD_TYPES or not location:
            flash("Select a valid blood group and enter a location.")
            return redirect(url_for("search"))

        connection = get_db_connection()

        try:
            cursor = connection.cursor()

            # Do not expose donor phone numbers in search results.
            cursor.execute(
                """
                SELECT
                    name,
                    NULL AS contact,
                    blood_type,
                    location
                FROM donors
                WHERE location = ?
                  AND availability = ?
                  AND eligible = 1
                ORDER BY id DESC
                """,
                (location, AVAILABLE),
            )

            all_donors = cursor.fetchall()

            # Match each donor's blood type against the requested
            # recipient blood type.
            donors = [
                row
                for row in all_donors
                if (
                    row[2] in BLOOD_COMPATIBILITY
                    and blood_type in BLOOD_COMPATIBILITY[row[2]]
                )
            ]

        finally:
            connection.close()

    return render_template("search.html", donors=donors)


# =========================================================
# 16. EMERGENCY BLOOD REQUESTS
# =========================================================

# The endpoint is explicitly named "request_blood" to match
# the dashboard.html and emergency.html templates.
@app.route(
    "/request",
    methods=["GET", "POST"],
    endpoint="request_blood",
)
@login_required
def blood_request():
    user_id = session["user_id"]

    if request.method == "POST":
        blood_type = form_text("blood_type", 3)
        urgency = form_text("urgency", 20)
        location = form_text("location", 150)
        hospital = form_text("hospital", 150)
        contact = form_text("contact", 30)

        if (
            blood_type not in BLOOD_TYPES
            or urgency not in URGENCY_LEVELS
            or not location
            or not hospital
            or not valid_phone(contact)
        ):
            flash(
                "Check the blood group, urgency, location, "
                "hospital, and contact number."
            )
            return redirect(url_for("request_blood"))

        connection = get_db_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO blood_requests
                    (
                        blood_type,
                        urgency,
                        location,
                        hospital,
                        contact,
                        user_id
                    )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    blood_type,
                    urgency,
                    location,
                    hospital,
                    contact,
                    user_id,
                ),
            )

            for donor_blood_type, compatible_recipients in (
                BLOOD_COMPATIBILITY.items()
            ):
                if blood_type not in compatible_recipients:
                    continue

                cursor.execute(
                    """
                    SELECT DISTINCT user_id
                    FROM donors
                    WHERE blood_type = ?
                      AND location = ?
                      AND availability = ?
                      AND eligible = 1
                      AND user_id IS NOT NULL
                    """,
                    (
                        donor_blood_type,
                        location,
                        AVAILABLE,
                    ),
                )

                for donor_user in cursor.fetchall():
                    donor_user_id = donor_user[0]

                    if donor_user_id != user_id:
                        create_notification(
                            connection,
                            donor_user_id,
                            (
                                f"Blood request: {blood_type} "
                                f"needed in {location}."
                            ),
                            "blood_request",
                        )

            connection.commit()
            flash("Blood request posted successfully.")

        except Exception:
            connection.rollback()
            app.logger.exception("Blood request creation failed")
            flash("Unable to create the blood request.")

        finally:
            connection.close()

        return redirect(url_for("dashboard"))

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        # Column order:
        # 0 id, 1 blood_type, 2 urgency, 3 location,
        # 4 hospital, 5 contact, 6 status, 7 owner user_id.
        # Only the owner receives the request's contact number.
        cursor.execute(
            """
            SELECT
                id,
                blood_type,
                urgency,
                location,
                hospital,
                CASE WHEN user_id = ? THEN contact ELSE NULL END,
                status,
                user_id
            FROM blood_requests
            WHERE status = 'Pending'
            ORDER BY id DESC
            """,
            (user_id,),
        )

        requests_list = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "emergency.html",
        requests=requests_list,
        current_user_id=user_id,
    )


# =========================================================
# 17. FULFIL REQUEST — OWNER ONLY
# =========================================================

@app.route(
    "/fulfill/<int:request_id>",
    methods=["POST"],
)
@login_required
def fulfill_request(request_id):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE blood_requests
            SET status = 'Fulfilled'
            WHERE id = ?
              AND user_id = ?
              AND status = 'Pending'
            """,
            (
                request_id,
                session["user_id"],
            ),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            flash(
                "Request not found or you are not authorized "
                "to fulfill it."
            )

        else:
            connection.commit()
            flash("Your blood request has been marked as fulfilled.")

    except Exception:
        connection.rollback()
        app.logger.exception("Request fulfillment failed")
        flash("Unable to fulfill the request.")

    finally:
        connection.close()

    return redirect(url_for("request_blood"))


# =========================================================
# 18. SIGNUP
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

    password = request.form.get("password") or ""

    if not name:
        flash("Please enter your name.")
        return redirect(url_for("signup"))

    if not email and not phone:
        flash("Please enter an email address or phone number.")
        return redirect(url_for("signup"))

    if email and not valid_email(email):
        flash("Please enter a valid email address.")
        return redirect(url_for("signup"))

    if phone and not valid_phone(phone):
        flash("Please enter a valid phone number.")
        return redirect(url_for("signup"))

    if len(password) < 8 or len(password) > 128:
        flash("Password must be between 8 and 128 characters.")
        return redirect(url_for("signup"))

    hashed_password = generate_password_hash(password)

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, phone, password)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email or None,
                phone or None,
                hashed_password,
            ),
        )

        connection.commit()
        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    except Exception:
        connection.rollback()
        app.logger.exception("Signup failed")
        flash(
            "Unable to create account. Check whether "
            "the email or phone number is already registered."
        )

    finally:
        connection.close()

    return redirect(url_for("signup"))


# =========================================================
# 19. LOGIN
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
        flash("Enter your email/phone and password.")
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, password
            FROM users
            WHERE lower(email) = ? OR phone = ?
            """,
            (
                login_input.lower(),
                login_input,
            ),
        )

        user = cursor.fetchone()

    finally:
        connection.close()

    if user and check_password_hash(user[2], password):
        # Rotate session and CSRF token after authentication.
        session.clear()

        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session.permanent = True
        session["_csrf_token"] = secrets.token_urlsafe(32)

        flash("Login successful.")
        return redirect(url_for("dashboard"))

    flash("Invalid email/phone or password.")
    return redirect(url_for("login"))


# =========================================================
# 20. LOGOUT — POST ONLY
# =========================================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))


# =========================================================
# 21. NOTIFICATIONS — CURRENT USER ONLY
# =========================================================

@app.route("/notifications")
@login_required
def notifications():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                message,
                notification_type,
                created_at,
                is_read
            FROM notifications
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],),
        )

        notifications_list = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "notifications.html",
        notifications=notifications_list,
    )


# =========================================================
# 22. ERROR HANDLERS
# =========================================================

@app.errorhandler(400)
def bad_request(error):
    return (
        "Bad request. A required security token may be missing "
        "or invalid. Please refresh the page and try again.",
        400,
    )


@app.errorhandler(413)
def request_too_large(error):
    return "Submitted request is too large.", 413


# =========================================================
# 23. INITIALIZE DATABASE
# =========================================================

init_database()


if __name__ == "__main__":
    app.run()
