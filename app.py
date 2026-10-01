from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

# Flask 앱 생성
app = Flask(__name__)


# 데이터베이스와 memo 테이블 생성
def create_table():
    connect_db = sqlite3.connect("memo.db")
    cursor = connect_db.cursor()

    # memo 테이블이 없으면 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    connect_db.commit()
    connect_db.close()


# 메인 페이지
# 메모 목록, 검색, 분류 기능 처리
@app.route("/")
def index():

    # 검색어와 분류 값 받기
    search = request.args.get("search", "")
    category = request.args.get("category", "")

    # 데이터베이스 연결
    conn = sqlite3.connect("memo.db")

    # 컬럼 이름으로 데이터를 사용할 수 있게 설정
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 제목과 분류를 같이 검색
    if search and category:
        cursor.execute("""
            SELECT * FROM memo
            WHERE title LIKE ? AND category = ?
            ORDER BY id DESC
        """, ("%" + search + "%", category))

    # 제목만 검색
    elif search:
        cursor.execute("""
            SELECT * FROM memo
            WHERE title LIKE ?
            ORDER BY id DESC
        """, ("%" + search + "%",))

    # 분류만 검색
    elif category:
        cursor.execute("""
            SELECT * FROM memo
            WHERE category = ?
            ORDER BY id DESC
        """, (category,))

    # 검색 조건이 없으면 전체 메모 조회
    else:
        cursor.execute("""
            SELECT * FROM memo
            ORDER BY id DESC
        """)

    # 조회한 메모 데이터 가져오기
    memos = cursor.fetchall()

    conn.close()

    # index.html에 데이터 전달
    return render_template(
        "index.html",
        memos=memos,
        search=search,
        category=category
    )


# 새 메모 작성
@app.route("/add", methods=["GET", "POST"])
def add():

    # 저장 버튼을 눌렀을 때 실행
    if request.method == "POST":

        # HTML form에서 데이터 받기
        title = request.form["title"]
        content = request.form["content"]
        category = request.form["category"]
        amount = request.form["amount"]

        # 생활이 아니면 금액을 저장하지 않음
        if category != "생활":
            amount = None

        # 금액을 입력하지 않은 경우
        elif amount == "":
            amount = None

        # 현재 날짜 저장
        created_at = datetime.now().strftime("%Y-%m-%d")

        # 데이터베이스 연결
        conn = sqlite3.connect("memo.db")
        cursor = conn.cursor()

        # 새로운 메모 저장
        cursor.execute("""
            INSERT INTO memo
            (title, content, category, amount, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            content,
            category,
            amount,
            created_at,
            created_at
        ))

        conn.commit()
        conn.close()

        # 저장 후 메인 페이지로 이동
        return redirect("/")

    # GET 방식이면 작성 페이지 표시
    return render_template("add.html")


# 메모 수정
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    # 데이터베이스 연결
    conn = sqlite3.connect("memo.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 수정 완료 버튼을 눌렀을 때 실행
    if request.method == "POST":

        # 수정된 데이터 받기
        title = request.form["title"]
        content = request.form["content"]
        category = request.form["category"]
        amount = request.form["amount"]

        # 생활이 아니면 금액 삭제
        if category != "생활":
            amount = None

        elif amount == "":
            amount = None

        # 수정 날짜 저장
        updated_at = datetime.now().strftime("%Y-%m-%d")

        # 선택한 메모 수정
        cursor.execute("""
            UPDATE memo
            SET title = ?,
                content = ?,
                category = ?,
                amount = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            title,
            content,
            category,
            amount,
            updated_at,
            id
        ))

        conn.commit()
        conn.close()

        # 수정 후 메인 페이지로 이동
        return redirect("/")

    # 수정할 메모 1개 가져오기
    cursor.execute(
        "SELECT * FROM memo WHERE id = ?",
        (id,)
    )

    memo = cursor.fetchone()

    conn.close()

    # edit.html에 수정할 메모 전달
    return render_template(
        "edit.html",
        memo=memo
    )


# 메모 삭제
@app.route("/delete/<int:id>")
def delete(id):

    # 데이터베이스 연결
    conn = sqlite3.connect("memo.db")
    cursor = conn.cursor()

    # 선택한 메모 삭제
    cursor.execute(
        "DELETE FROM memo WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    # 삭제 후 메인 페이지로 이동
    return redirect("/")


# 프로그램 실행
if __name__ == "__main__":

    # 시작할 때 테이블 생성
    create_table()

    # Flask 서버 실행
    app.run(debug=True)