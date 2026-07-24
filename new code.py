# ====================== STUDENT REPORT CARD SYSTEM ======================

import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, gold
from reportlab.lib.utils import ImageReader

# ---------------- DATABASE SETUP ----------------
con = sqlite3.connect("reportcard.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    roll INTEGER PRIMARY KEY,
    name TEXT,
    cls TEXT,
    math INTEGER DEFAULT 0,
    physics INTEGER DEFAULT 0,
    chemistry INTEGER DEFAULT 0,
    english INTEGER DEFAULT 0,
    computer INTEGER DEFAULT 0
)
""")
con.commit()

# ---------------- ADD STUDENT ----------------
def add_student():
    try:
        roll = int(input("Enter Roll Number: "))

        cur.execute("SELECT roll FROM students WHERE roll=?", (roll,))
        if cur.fetchone():
            print("✖ Roll number already exists!")
            return

        name = input("Enter Student Name: ")
        cls = input("Enter Class: ")

        cur.execute(
            "INSERT INTO students (roll, name, cls) VALUES (?, ?, ?)",
            (roll, name, cls)
        )
        con.commit()
        print("✔ Student added successfully!")

    except ValueError:
        print("✖ Invalid input! Roll must be a number.")

# ---------------- MARK INPUT VALIDATION ----------------
def get_mark(subject):
    while True:
        try:
            m = int(input(f"{subject}: "))
            if 0 <= m <= 100:
                return m
            else:
                print("✖ Enter marks between 0 and 100.")
        except ValueError:
            print("✖ Enter a valid number.")

# ---------------- ENTER MARKS ----------------
def enter_marks():
    try:
        roll = int(input("Enter Roll Number: "))

        cur.execute("SELECT roll FROM students WHERE roll=?", (roll,))
        if not cur.fetchone():
            print("✖ No student found with this roll number!")
            return

        print("Enter marks out of 100:")
        math = get_mark("Math")
        phy = get_mark("Physics")
        chem = get_mark("Chemistry")
        eng = get_mark("English")
        comp = get_mark("Computer")

        cur.execute("""
        UPDATE students SET
        math=?, physics=?, chemistry=?, english=?, computer=?
        WHERE roll=?
        """, (math, phy, chem, eng, comp, roll))

        con.commit()
        print("✔ Marks updated successfully!")

    except ValueError:
        print("✖ Invalid roll number!")

# ---------------- VIEW REPORT (TERMINAL) ----------------
def view_report(roll):
    cur.execute("SELECT * FROM students WHERE roll=?", (roll,))
    row = cur.fetchone()

    if row:
        total = sum(row[3:8])
        percent = total / 5

        if percent >= 90:
            grade = "A+"
        elif percent >= 80:
            grade = "A"
        elif percent >= 70:
            grade = "B"
        elif percent >= 60:
            grade = "C"
        else:
            grade = "D"

        print("\n------ REPORT CARD ------")
        print(f"Name: {row[1]} | Class: {row[2]} | Roll: {row[0]}")
        print("--------------------------")
        print(f"Math: {row[3]}")
        print(f"Physics: {row[4]}")
        print(f"Chemistry: {row[5]}")
        print(f"English: {row[6]}")
        print(f"Computer: {row[7]}")
        print("--------------------------")
        print(f"Total: {total} / 500")
        print(f"Percentage: {percent:.2f}%")
        print(f"Grade: {grade}")

    else:
        print("✖ No record found.")

# ---------------- VIEW ALL STUDENTS ----------------
def view_all():
    cur.execute("SELECT roll, name, cls FROM students")
    rows = cur.fetchall()

    if not rows:
        print("\nNo students found.")
        return

    print("\nAll Students:")
    for r in rows:
        print(f"Roll: {r[0]} | Name: {r[1]} | Class: {r[2]}")

# ---------------- PDF REPORT CARD ----------------
def generate_pdf(roll):
    cur.execute("SELECT * FROM students WHERE roll=?", (roll,))
    row = cur.fetchone()

    if not row:
        print("✖ Student not found!")
        return

    total = sum(row[3:8])
    percent = total / 5

    if percent >= 90:
        grade = "A+"
    elif percent >= 80:
        grade = "A"
    elif percent >= 70:
        grade = "B"
    elif percent >= 60:
        grade = "C"
    else:
        grade = "D"

    c = canvas.Canvas(f"Report_{roll}.pdf", pagesize=A4)

    # ---------- HEADER ----------
    try:
        logo = ImageReader("logo.png")
        c.drawImage(logo, 40, 690, width=120, height=120, preserveAspectRatio=True)
    except:
        c.setFont("Helvetica", 10)
        c.drawString(40, 760, "(Logo missing: place a file named 'logo.png')")

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(gold)
    c.drawString(180, 770, "JBG INTERNATIONAL SCHOOL")

    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawString(180, 750, "Near Chandauk Doraha Jahangirabad")
    c.drawString(180, 735, "BSR. (U.P.) PIN 203394")

    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.line(30, 720, 580, 720)

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 700, "STUDENT REPORT CARD")

    # ---------- STUDENT DETAILS ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 660, "Student Information")

    c.setFont("Helvetica", 12)
    c.drawString(60, 640, f"Name: {row[1]}")
    c.drawString(60, 620, f"Class: {row[2]}")
    c.drawString(60, 600, f"Roll Number: {row[0]}")

    # ---------- SUBJECT TABLE ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 570, "Marks Obtained")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(gold)
    c.rect(50, 535, 500, 25, fill=1)

    c.setFillColor(black)
    c.drawString(60, 545, "Subject")
    c.drawString(300, 545, "Marks")

    subjects = ["Math", "Physics", "Chemistry", "English", "Computer"]
    marks = row[3:8]

    y = 510
    c.setFont("Helvetica", 12)

    for sub, mark in zip(subjects, marks):
        c.drawString(60, y, sub)
        c.drawString(300, y, str(mark))
        y -= 25

    # ---------- TOTAL & GRADE ----------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 10, "Performance Summary")

    c.setFont("Helvetica", 12)
    c.drawString(60, y - 30, f"Total: {total} / 500")
    c.drawString(60, y - 50, f"Percentage: {percent:.2f}%")
    c.drawString(60, y - 70, f"Grade: {grade}")

    # ---------- SIGNATURES ----------
    c.setFont("Helvetica", 12)
    c.rect(60, 120, 150, 60)
    c.rect(360, 120, 150, 60)
    c.drawString(80, 100, "Class Teacher")
    c.drawString(395, 100, "Principal")

    c.save()
    print("✔ PDF Report Card Generated Successfully!")

# ---------------- MENU ----------------
while True:
    print("""
1. Add Student
2. Enter Marks
3. View Report (Terminal)
4. View All Students
5. Generate PDF Report Card
6. Exit
""")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_student()
    elif choice == "2":
        enter_marks()
    elif choice == "3":
        r = int(input("Enter Roll Number: "))
        view_report(r)
    elif choice == "4":
        view_all()
    elif choice == "5":
        r = int(input("Enter Roll Number: "))
        generate_pdf(r)
    elif choice == "6":
        print("Exiting program...")
        break
    else:
        print("Invalid choice!")

con.close()
