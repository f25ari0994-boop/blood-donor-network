from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import get_db_connection, init_database
from datetime import datetime, date
import os


# --------------------------------
# FLASK APP
# --------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key"
)


# --------------------------------
# BLOOD COMPATIBILITY
# --------------------------------

BLOOD_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}


# --------------------------------
# CREATE NOTIFICATION
# --------------------------------

def create_notification(
    connection,
    user_id,
    message,
    notification_type
):

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
    INSERT INTO notifications
    (
        user_id,
        message,
        notification_type,
        created_at
    )
    VALUES (?, ?, ?, ?)
    """, (
        user_id,
        message,
        notification_type,
        created_at
    ))


# --------------------------------
# CHECK 90-DAY ELIGIBILITY
# --------------------------------

def check_donor_eligibility(user_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id,
        name,
        last_donation,
        eligible
    FROM donors
    WHERE user_id = ?
    """, (user_id,))

    donors = cursor.fetchall()

    for donor in donors:

        donor_id = donor[0]
        donor_name = donor[1]
        last_donation = donor[2]
        eligible = donor[3]

        # No previous donation
        if not last_donation:
            continue

        try:

            donation_date = datetime.strptime(
                last_donation,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            continue

        days_since_donation = (
            date.today() - donation_date
        ).days

        # --------------------------------
        # 90 DAYS COMPLETED
        # --------------------------------

        if days_since_donation >= 90 and eligible == 0:

            cursor.execute("""
            UPDATE donors
            SET eligible = 1,
                availability = 'Available'
            WHERE id = ?
            """, (donor_id,))

            create_notification(
                connection,
                user_id,
                f"{donor_name} is eligible to donate blood again after 90 days.",
                "eligibility"
            )

    connection.commit()
    connection.close()


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():

    return redirect("/login")


# --------------------------------
# DASHBOARD
# --------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    check_donor_eligibility(
        session["user_id"]
    )

    return render_template(
        "dashboard.html",
        user_name=session["user_name"]
    )


# --------------------------------
# DONOR REGISTRATION
# --------------------------------
@app.route("/donor", methods=["GET", "POST"])
def donor():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        contact = request.form["contact"]
        blood_type = request.form["blood_type"]
        location = request.form["location"]

        availability = "Available"

        last_donation = request.form.get(
            "last_donation",
            ""
        )

        # --------------------------------
        # DUPLICATE DONOR CHECK
        # --------------------------------

        cursor.execute("""
        SELECT id
        FROM donors
        WHERE name = ?
        AND contact = ?
        """, (
            name,
            contact
        ))

        existing_donor = cursor.fetchone()

        if existing_donor:

            connection.close()

            flash(
                "This person is already registered as a donor!"
            )

            return redirect("/donor")

        # --------------------------------
        # CHECK 90-DAY ELIGIBILITY
        # --------------------------------

        eligible = 1

        if last_donation:

            try:

                donation_date = datetime.strptime(
                    last_donation,
                    "%Y-%m-%d"
                ).date()

                days_since_donation = (
                    date.today() - donation_date
                ).days

                if days_since_donation < 90:

                    eligible = 0
                    availability = "Not Available"

            except ValueError:

                connection.close()

                flash(
                    "Invalid donation date."
                )

                return redirect("/donor")

        # --------------------------------
        # SAVE DONOR
        # --------------------------------

        cursor.execute("""
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
        """, (
            name,
            age,
            contact,
            blood_type,
            location,
            availability,
            last_donation,
            eligible,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        flash(
            "Donor registered successfully!"
        )

        return redirect("/donor")

    connection.close()

    return render_template(
        "donor.html"
    )
# --------------------------------
# DONOR LIST
# --------------------------------

@app.route("/donor-list")
def donor_list():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    # Check current user's eligibility
    check_donor_eligibility(
        session["user_id"]
    )

    cursor.execute("""
    SELECT id,
        name,
        age,
        contact,
        blood_type,
        location,
        availability,
        eligible
    FROM donors
    ORDER BY id DESC
    """)

    donors = cursor.fetchall()

    connection.close()

    return render_template(
        "donor_list.html",
        donors=donors
    )


# --------------------------------
# REPORT DONATION
# --------------------------------

@app.route(
    "/report-donation/<int:donor_id>",
    methods=["GET", "POST"]
)
def report_donation(donor_id):

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    # --------------------------------
    # CHECK DONOR OWNERSHIP
    # --------------------------------

    cursor.execute("""
    SELECT id,
        name,
        blood_type
    FROM donors
    WHERE id = ?
    AND user_id = ?
    """, (
        donor_id,
        session["user_id"]
    ))

    donor = cursor.fetchone()

    if not donor:

        connection.close()

        flash(
            "You are not allowed to manage this donor."
        )

        return redirect("/donor-list")

    # --------------------------------
    # FORM SUBMITTED
    # --------------------------------

    if request.method == "POST":

        donation_date = request.form[
            "donation_date"
        ]

        hospital = request.form[
            "hospital"
        ]

        location = request.form[
            "location"
        ]

        # --------------------------------
        # SAVE DONATION
        # --------------------------------

        cursor.execute("""
        INSERT INTO donations
        (
            donor_id,
            donation_date,
            hospital,
            location
        )
        VALUES (?, ?, ?, ?)
        """, (
            donor_id,
            donation_date,
            hospital,
            location
        ))

        # --------------------------------
        # UPDATE DONOR
        # --------------------------------

        cursor.execute("""
        UPDATE donors
        SET last_donation = ?,
            eligible = 0,
            availability = 'Not Available'
        WHERE id = ?
        AND user_id = ?
        """, (
            donation_date,
            donor_id,
            session["user_id"]
        ))

        connection.commit()
        connection.close()

        flash(
            "Donation reported successfully!"
        )

        return redirect("/donor-list")

    connection.close()

    return render_template(
        "report_donation.html",
        donor=donor
    )


# --------------------------------
# TOGGLE AVAILABILITY
# --------------------------------

@app.route(
    "/toggle-availability/<int:donor_id>",
    methods=["POST"]
)
def toggle_availability(donor_id):

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    # --------------------------------
    # CHECK DONOR OWNERSHIP
    # --------------------------------

    cursor.execute("""
    SELECT availability
    FROM donors
    WHERE id = ?
    AND user_id = ?
    """, (
        donor_id,
        session["user_id"]
    ))

    donor = cursor.fetchone()

    if not donor:

        connection.close()

        flash(
            "You are not allowed to modify this donor."
        )

        return redirect("/donor-list")

    # --------------------------------
    # CHANGE AVAILABILITY
    # --------------------------------

    if donor[0] == "Available":

        new_status = "Not Available"

    else:

        new_status = "Available"

    cursor.execute("""
    UPDATE donors
    SET availability = ?
    WHERE id = ?
    AND user_id = ?
    """, (
        new_status,
        donor_id,
        session["user_id"]
    ))

    connection.commit()
    connection.close()

    return redirect("/donor-list")


# --------------------------------
# SEARCH DONORS
# --------------------------------

@app.route("/search", methods=["GET", "POST"])
def search():

    if "user_id" not in session:
        return redirect("/login")

    donors = []

    if request.method == "POST":

        blood_type = request.form[
            "blood_type"
        ]

        location = request.form[
            "location"
        ]

        connection = sqlite3.connect(
            "database/blood_network.db"
        )

        cursor = connection.cursor()

        cursor.execute("""
        SELECT name,
            contact,
            blood_type,
            location
        FROM donors
        WHERE location = ?
        AND availability = 'Available'
        AND eligible = 1
        """, (
            location,
        ))

        all_donors = cursor.fetchall()

        # --------------------------------
        # BLOOD COMPATIBILITY
        # --------------------------------

        for donor in all_donors:

            donor_blood_type = donor[2]

            if blood_type in BLOOD_COMPATIBILITY[
                donor_blood_type
            ]:

                donors.append(donor)

        connection.close()

    return render_template(
        "search.html",
        donors=donors
    )


# --------------------------------
# EMERGENCY BLOOD REQUEST
# --------------------------------

@app.route(
    "/request",
    methods=["GET", "POST"]
)
def blood_request():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    if request.method == "POST":

        blood_type = request.form[
            "blood_type"
        ]

        urgency = request.form[
            "urgency"
        ]

        location = request.form[
            "location"
        ]

        hospital = request.form[
            "hospital"
        ]

        contact = request.form[
            "contact"
        ]

        # --------------------------------
        # SAVE BLOOD REQUEST
        # --------------------------------

        cursor.execute("""
        INSERT INTO blood_requests
        (
            blood_type,
            urgency,
            location,
            hospital,
            contact
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            blood_type,
            urgency,
            location,
            hospital,
            contact
        ))

        connection.commit()

        # --------------------------------
        # NOTIFY MATCHING DONORS
        # --------------------------------

        for donor_blood_type in BLOOD_COMPATIBILITY:

            if blood_type in BLOOD_COMPATIBILITY[
                donor_blood_type
            ]:

                cursor.execute("""
                SELECT user_id
                FROM donors
                WHERE blood_type = ?
                AND location = ?
                AND availability = 'Available'
                AND eligible = 1
                AND user_id IS NOT NULL
                """, (
                    donor_blood_type,
                    location
                ))

                matching_donors = cursor.fetchall()

                for donor in matching_donors:

                    create_notification(
                        connection,
                        donor[0],
                        f"Emergency blood request: {blood_type} needed in {location}.",
                        "blood_request"
                    )

        connection.commit()
        connection.close()

        flash(
            "Blood request posted successfully!"
        )

        # --------------------------------
        # REDIRECT AFTER SUBMIT
        # --------------------------------

        return redirect("/dashboard")

    # --------------------------------
    # GET PENDING REQUESTS
    # --------------------------------

    cursor.execute("""
    SELECT id,
        blood_type,
        urgency,
        location,
        hospital,
        contact,
        status
    FROM blood_requests
    WHERE status = 'Pending'
    ORDER BY id DESC
    """)

    requests_list = cursor.fetchall()

    connection.close()

    return render_template(
        "emergency.html",
        requests=requests_list
    )


# --------------------------------
# MARK REQUEST AS FULFILLED
# --------------------------------

@app.route(
    "/fulfill/<int:request_id>",
    methods=["POST"]
)
def fulfill_request(request_id):

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE blood_requests
    SET status = 'Fulfilled'
    WHERE id = ?
    """, (
        request_id,
    ))

    connection.commit()
    connection.close()

    flash(
        "Blood request marked as fulfilled!"
    )

    return redirect("/request")


# --------------------------------
# SIGNUP
# --------------------------------

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form[
            "name"
        ]

        email = request.form[
            "email"
        ].strip()

        phone = request.form[
            "phone"
        ].strip()

        password = request.form[
            "password"
        ]

        # --------------------------------
        # EMAIL OR PHONE REQUIRED
        # --------------------------------

        if not email and not phone:

            flash(
                "Please enter an email or phone number!"
            )

            return render_template(
                "signup.html"
            )

        # --------------------------------
        # HASH PASSWORD
        # --------------------------------

        hashed_password = generate_password_hash(
            password
        )

        connection = sqlite3.connect(
            "database/blood_network.db"
        )

        cursor = connection.cursor()

        try:

            cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                phone,
                password
            )
            VALUES (?, ?, ?, ?)
            """, (
                name,
                email if email else None,
                phone if phone else None,
                hashed_password
            ))

            connection.commit()

            flash(
                "Account created successfully!"
            )

            return redirect("/login")

        except sqlite3.IntegrityError:

            flash(
                "Email or phone number already exists!"
            )

        finally:

            connection.close()

    return render_template(
        "signup.html"
    )


# --------------------------------
# LOGIN
# --------------------------------

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        login_input = request.form[
            "login_input"
        ].strip()

        password = request.form[
            "password"
        ]

        connection = sqlite3.connect(
            "database/blood_network.db"
        )

        cursor = connection.cursor()

        cursor.execute("""
        SELECT id,
            name,
            password
        FROM users
        WHERE email = ?
        OR phone = ?
        """, (
            login_input,
            login_input
        ))

        user = cursor.fetchone()

        connection.close()

        # --------------------------------
        # CHECK LOGIN
        # --------------------------------

        if user and check_password_hash(
            user[2],
            password
        ):

            session["user_id"] = user[0]

            session["user_name"] = user[1]

            flash(
                "Login successful!"
            )

            return redirect(
                "/dashboard"
            )

        else:

            flash(
                "Invalid email/phone or password!"
            )

    return render_template(
        "login.html"
    )


# --------------------------------
# LOGOUT
# --------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out!"
    )

    return redirect("/")


# --------------------------------
# NOTIFICATIONS
# --------------------------------

@app.route("/notifications")
def notifications():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
    SELECT id,
        message,
        notification_type,
        created_at,
        is_read
    FROM notifications
    WHERE user_id = ?
    ORDER BY id DESC
    """, (
        session["user_id"],
    ))

    notifications_list = cursor.fetchall()

    connection.close()

    return render_template(
        "notifications.html",
        notifications=notifications_list
    )


# --------------------------------
# START FLASK SERVER
# --------------------------------
if __name__ == "__main__":
    init_database()
    app.run()
    