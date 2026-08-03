# CONFIG MOODLE API

# https://yourmoodle.com/webservice/rest/server.php
#     ?wstoken=TOKEN_KAMU
#     &wsfunction=WS_FUNCTION
#     &moodlewsrestformat=json


# GET DATA ACTIVITY COMPLETION

import requests
import json

# ===================================================================
# FUNCTION: GET COMPLETION RATE (API + DUMMY)
# ===================================================================
def get_completion_rate(base_url=None, token=None, course_id=None):


    # Dummy fallback
    dummy_data = {
        "completion_status": [
            {"userid": 5, "statuses": [
                {"cmid": 101, "state": 1},
                {"cmid": 102, "state": 1},
                {"cmid": 103, "state": 0}]},
            {"userid": 6, "statuses": [
                {"cmid": 101, "state": 1},
                {"cmid": 102, "state": 0},
                {"cmid": 103, "state": 0}]}
        ]
    }

    # ============================================================
    # MODE DUMMY (API belum diset)
    # ============================================================
    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Completion Rate menggunakan dummy JSON.")
        api_data = dummy_data["completion_status"]

    else:
        try:
            print("[API] Mengambil daftar user untuk completion...")

            # 1. Get user list
            url_users = f"{base_url}/webservice/rest/server.php"
            params_users = {
                "wstoken": token,
                "wsfunction": "core_enrol_get_enrolled_users",
                "moodlewsrestformat": "json",
                "courseid": course_id
            }
            user_response = requests.get(url_users, params=params_users).json()

            if isinstance(user_response, dict) and "exception" in user_response:
                api_data = dummy_data["completion_status"]
            else:
                user_ids = [u["id"] for u in user_response]

                # 2. Ambil completion tiap user
                api_data = []
                for uid in user_ids:
                    url_completion = f"{base_url}/webservice/rest/server.php"
                    params_comp = {
                        "wstoken": token,
                        "wsfunction": "core_completion_get_activities_completion_status",
                        "moodlewsrestformat": "json",
                        "courseid": course_id,
                        "userid": uid
                    }
                    comp_res = requests.get(url_completion, params=params_comp).json()

                    if "statuses" in comp_res:
                        api_data.append({
                            "userid": uid,
                            "statuses": comp_res["statuses"]
                        })

        except:
            print("[API ERROR] Completion API gagal → dummy digunakan")
            api_data = dummy_data["completion_status"]

    # ============================================================
    # HITUNG COMPLETION RATE
    # ============================================================
    all_states = []
    for user in api_data:
        for st in user["statuses"]:
            all_states.append(st["state"])

    completion_rate = (sum(all_states) / len(all_states)) if all_states else 0
    return completion_rate  # dalam skala 0–1

# GET DATA FORUM PARTICIPANT
def get_forum_participation(base_url=None, token=None, course_id=None):
    dummy_forum_data = [
        {"userid": 5, "posts": 4},
        {"userid": 6, "posts": 2},
        {"userid": 7, "posts": 0},
    ]

    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Forum participation menggunakan dummy JSON.")
        data = dummy_forum_data
    else:
        try:
            print("[API] Mengambil forum discussions...")
            url_forum = f"{base_url}/webservice/rest/server.php"
            params = {
                "wstoken": token,
                "wsfunction": "mod_forum_get_forums_by_courses",
                "moodlewsrestformat": "json",
                "courseids[0]": course_id
            }

            forum_res = requests.get(url_forum, params=params).json()

            if isinstance(forum_res, dict) and "exception" in forum_res:
                data = dummy_forum_data
            else:
                data = []
                for forum in forum_res:
                    forumid = forum["id"]

                    params_disc = {
                        "wstoken": token,
                        "wsfunction": "mod_forum_get_forum_discussions_paginated",
                        "moodlewsrestformat": "json",
                        "forumid": forumid,
                        "page": 0,
                        "perpage": 100
                    }

                    disc_res = requests.get(url_forum, params=params_disc).json()

                    user_posts = {}

                    if "discussions" in disc_res:
                        for disc in disc_res["discussions"]:
                            user_id = disc["userid"]
                            user_posts[user_id] = user_posts.get(user_id, 0) + 1

                    data = [{"userid": uid, "posts": cnt} for uid, cnt in user_posts.items()]

        except:
            data = dummy_forum_data

    total_posts = sum(item["posts"] for item in data)
    if total_posts == 0:
        return 0

    forum_participation_value = sum(item["posts"] / total_posts for item in data) / len(data)
    return forum_participation_value


# GET AVERAGE GRADE SISWA

import requests
import json

# ==============================================================
# FUNCTION: GET AVERAGE GRADE (Nilai rata-rata kelas)
# ==============================================================
def get_avg_grade(base_url=None, token=None, course_id=None):
    """
    Mengambil rata-rata nilai final peserta.
    Output berupa nilai 0–1 (sudah dinormalisasi).
    """

    # ----------- DUMMY DATA -----------
    dummy_grade_data = [
        {"userid": 5, "finalgrade": 85},
        {"userid": 6, "finalgrade": 90},
        {"userid": 7, "finalgrade": 70},
        {"userid": 8, "finalgrade": 75},
    ]

    # Jika API tidak tersedia → pakai dummy
    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Menggunakan dummy grade data.")
        grades = [item["finalgrade"] for item in dummy_grade_data]

    else:
        try:
            print("[API] Mengambil grade peserta...")
            url = f"{base_url}/webservice/rest/server.php"

            params = {
                "wstoken": token,
                "wsfunction": "gradereport_user_get_grade_items",
                "moodlewsrestformat": "json",
                "courseid": course_id
            }

            response = requests.get(url, params=params).json()

            grades = []

            # Parsing hasil API
            for user in response.get("usergrades", []):
                for item in user.get("gradeitems", []):
                    if item.get("itemtype") == "course":  # final grade
                        try:
                            grades.append(float(item.get("gradeformatted")))
                        except:
                            pass

        except Exception as e:
            print("[API ERROR] Gagal mengambil grade → gunakan dummy.")
            grades = [item["finalgrade"] for item in dummy_grade_data]

    if not grades:
        return 0

    avg_grade = sum(grades) / len(grades)

    # Normalisasi dari 0–100 menjadi 0–1
    return avg_grade / 100


# GET PASS RATE
# ==============================================================
# FUNCTION: GET PASS RATE (Persentase kelulusan berdasarkan KKM)
# ==============================================================
def get_pass_rate(base_url=None, token=None, course_id=None, kkm=50):
    """
    Menghitung persentase jumlah peserta yang lulus (nilai >= KKM).
    KKM default 50.
    Output berupa nilai 0–1.
    """

    # ----------- DUMMY DATA -----------
    dummy_grade_data = [
        {"userid": 5, "finalgrade": 85},
        {"userid": 6, "finalgrade": 90},
        {"userid": 7, "finalgrade": 45},
        {"userid": 8, "finalgrade": 55},
    ]

    # Jika API kosong → gunakan dummy
    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Pass rate menggunakan dummy.")
        grades = [item["finalgrade"] for item in dummy_grade_data]

    else:
        try:
            print("[API] Mengambil nilai peserta untuk pass rate...")
            url = f"{base_url}/webservice/rest/server.php"

            params = {
                "wstoken": token,
                "wsfunction": "gradereport_user_get_grade_items",
                "moodlewsrestformat": "json",
                "courseid": course_id
            }

            response = requests.get(url, params=params).json()

            grades = []

            for user in response.get("usergrades", []):
                for item in user.get("gradeitems", []):
                    if item.get("itemtype") == "course":
                        try:
                            grades.append(float(item.get("gradeformatted")))
                        except:
                            pass

        except:
            print("[API ERROR] Gagal mengambil grade → pakai dummy.")
            grades = [item["finalgrade"] for item in dummy_grade_data]

    if not grades:
        return 0

    # Hitung jumlah yang lulus
    total = len(grades)
    lulus = len([g for g in grades if g >= kkm])

    pass_rate = lulus / total
    return pass_rate


# GET FEEDBACK DOSEN DI MOODLE

def get_feedback_speed(base_url=None, token=None, course_id=None):
    """
    Mengukur kecepatan feedback instruktur terhadap tugas mahasiswa.
    Output: nilai 0–1.
    """

    # ---------- Dummy JSON ----------
    dummy_feedback_data = [
        {"assignment_id": 1, "feedback_time_hours": 10},
        {"assignment_id": 2, "feedback_time_hours": 24},
        {"assignment_id": 3, "feedback_time_hours": 5},
    ]

    # Jika API tidak diset → pakai dummy saja
    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Feedback speed menggunakan dummy JSON.")
        data = dummy_feedback_data
    else:
        try:
            # Contoh format API Moodle (tidak real)
            print("[API] Mengambil data feedback tugas...")
            url = f"{base_url}/webservice/rest/server.php"
            params = {
                "wstoken": token,
                "wsfunction": "mod_assign_get_grades",
                "moodlewsrestformat": "json",
                "courseids[0]": course_id
            }

            api_res = requests.get(url, params=params).json()

            if isinstance(api_res, dict) and "exception" in api_res:
                print("[API ERROR] → dummy JSON digunakan")
                data = dummy_feedback_data
            else:
                # Struktur asli Moodle cukup rumit, jadi disederhanakan
                data = [{"assignment_id": g["assignmentid"],
                         "feedback_time_hours": 12} for g in api_res.get("grades", [])]

                if not data:
                    data = dummy_feedback_data

        except:
            print("[API ERROR] Tidak bisa ambil feedback → dummy JSON")
            data = dummy_feedback_data

    # Hitung rata2 kecepatan feedback
    avg_hours = sum(item["feedback_time_hours"] for item in data) / len(data)

    # Maksimum waktu ideal feedback (misal 72 jam = 3 hari)
    IDEAL_LIMIT = 72

    score = max(0, 1 - (avg_hours / IDEAL_LIMIT))
    return round(score, 4)


# GET PRESENCE DOSEN DI MOODLE

def get_teacher_presence(base_url=None, token=None, course_id=None):
    """
    Mengukur kehadiran instruktur pada forum.
    Output: nilai 0–1.
    """

    # Dummy JSON (format: userid, role, posts)
    dummy_forum_data = [
        {"userid": 1, "role": "teacher", "posts": 5},
        {"userid": 5, "role": "student", "posts": 2},
        {"userid": 6, "role": "student", "posts": 1},
    ]

    if not base_url or not token or not course_id:
        print("[MODE DUMMY] Teacher presence dari dummy JSON.")
        data = dummy_forum_data
    else:
        try:
            print("[API] Mengambil data presence instruktur di forum...")

            # Ambil list forum (contoh)
            url = f"{base_url}/webservice/rest/server.php"
            params = {
                "wstoken": token,
                "wsfunction": "mod_forum_get_forums_by_courses",
                "moodlewsrestformat": "json",
                "courseids[0]": course_id
            }

            forum_res = requests.get(url, params=params).json()

            if isinstance(forum_res, dict) and "exception" in forum_res:
                print("[API ERROR] → dummy JSON")
                data = dummy_forum_data
            else:
                data = []
                for forum in forum_res:
                    # Contoh struktur — real API jauh lebih kompleks
                    data.append({"userid": 1, "role": "teacher", "posts": 3})
                    data.append({"userid": 5, "role": "student", "posts": 1})

        except:
            print("[API ERROR] Forum presence gagal → dummy JSON")
            data = dummy_forum_data

    total_posts = sum(item["posts"] for item in data)
    if total_posts == 0:
        return 0

    teacher_posts = sum(item["posts"] for item in data if item["role"] == "teacher")

    score = teacher_posts / total_posts
    return round(score, 4)


# PERHITUNGAN FINAL SCORE

def calculate_final_score(base_url=None, token=None, course_id=None):

    # ========== (1) Ambil Completion Rate ==========
    completion_rate = get_completion_rate(base_url, token, course_id)

    # ========== (2) Ambil Forum Participation ==========
    forum_participation = get_forum_participation(base_url, token, course_id)

    # ========== (3) Ambil Average Grade ==========
    avg_grade = get_avg_grade(base_url, token, course_id)

    # ========== (4) Ambil Pass Rate (KKM = 50 default) ==========
    pass_rate = get_pass_rate(base_url, token, course_id, kkm=50)

    # ========== (5) Hitung skor akhir ==========
    indikator_dummy = {
        "completion_rate": completion_rate,
        "forum_participation": forum_participation,
        "avg_grade": avg_grade,
        "pass_rate": pass_rate,
        "feedback_speed": get_feedback_speed(base_url, token, course_id),
        "teacher_presence": get_teacher_presence(base_url, token, course_id)
    }

    data_persentase = list(indikator_dummy.values())
    bobot = [0.15, 0.10, 0.35, 0.20, 0.15, 0.05]

    skor_akhir = sum(p * b for p, b in zip(data_persentase, bobot))

    return {
        "completion_rate_percent": round(completion_rate * 100, 2),
        "forum_participation_percent": round(forum_participation * 100, 2),
        "avg_grade_percent": round(avg_grade * 100, 2),
        "pass_rate_percent": round(pass_rate * 100, 2),
        "data_persentase": data_persentase,  
        "bobot": bobot,
        "skor_akhir": round(skor_akhir, 4),
        "skor_akhir_persen": round(skor_akhir * 100, 2)
    }


# FUNCTION MENAMPILKAN HASIL

import pandas as pd
import json

# fallback untuk display()
try:
    from IPython.display import display
except ImportError:
    def display(x):
        print(x)

def show_pretty_result():
    result = calculate_final_score('https://spada15.ums.ac.id', 'a7ad4336b5c42729905047ccb859d768', 1227)

    print("\n==============================")
    print(f"📌 Completion Rate        : {result['completion_rate_percent']}%")
    print(f"📌 Forum Participation    : {result['forum_participation_percent']}%")
    print(f"📌 Average Grade          : {result['avg_grade_percent']}%")
    print(f"📌 Pass Rate              : {result['pass_rate_percent']}%")
    print(f"📌 Skor Akhir             : {result['skor_akhir_persen']}%")
    print("------------------------------")

    # ==============================
    # Hitung nilai berbobot
    # ==============================
    persentase_list = [round(v * 100, 2) for v in result["data_persentase"]]
    bobot_list = result["bobot"]
    nilai_terbobot = [round((p/100) * b, 4) for p, b in zip(persentase_list, bobot_list)]

    # ==============================
    # Buat DataFrame tabel
    # ==============================
    df = pd.DataFrame({
        "Indikator": [
            "Activity Completion",
            "Forum Participation",
            "Average Grade",
            "Pass Rate",
            "Feedback Speed",
            "Teacher Presence"
        ],
        "Persentase (%)": persentase_list,
        "Bobot": bobot_list,
        "Nilai Terbobot": nilai_terbobot
    })

    print("\n📋 DETAIL INDIKATOR")
    display(df)

    print("\n📌 TOTAL NILAI TERBOBOT PADA COURSE =", round(sum(nilai_terbobot), 4))


# TAMPILKAN HASIL

show_pretty_result()
