# -*- coding: utf-8 -*-
"""세션 서비스 테스트. 실제 문제 은행을 쓰고 풀이 폴더만 임시 폴더로 돌림.

실행: python -m unittest discover -s tests
"""
import ast
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adaptive  # noqa: E402
import session  # noqa: E402
import study  # noqa: E402


def right_answer(sess, view):
    """문항의 정답(퀴즈) 또는 모범 답안(코드)."""
    it = sess.cat[view["key"]]
    if it["kind"] == "quiz":
        q = it["q"]
        if q["type"] == "choice":
            return q["answer"] if len(q["answer"]) > 1 else q["answer"][0]
        return q["answer"] if q["type"] == "output" else q["answer"][0]
    return it["set"]["secrets"][it["spec"]["id"] + "/solution.py"]


def wrong_answer(view):
    if view["kind"] == "code":
        return "print('오답')\n"
    return 9 if view["type"] == "choice" else "틀린 답"


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="study_test_")
        self._saved = (study.SUBMISSIONS_DIR, study.USER_FILE, os.environ.pop("STUDY_USER", None))
        study.SUBMISSIONS_DIR = os.path.join(self.tmp, "submissions")
        study.USER_FILE = os.path.join(self.tmp, ".study_user")
        self.sess = session.Session("tester")

    def tearDown(self):
        study.SUBMISSIONS_DIR, study.USER_FILE, user = self._saved
        if user is not None:
            os.environ["STUDY_USER"] = user
        shutil.rmtree(self.tmp, ignore_errors=True)

    def answer_all(self, rid, correct=True, only=None):
        for view in self.sess.open_round(rid)["items"]:
            if only is not None and view["no"] not in only:
                continue
            self.sess.set_answer(rid, view["id"], right_answer(self.sess, view) if correct else wrong_answer(view))

    def first_real_round(self):
        """진단을 미응답으로 확정해 코드 문제가 섞인 1회차를 만듦."""
        rnd, _ = self.sess.ensure_round()
        result = self.sess.grade(rnd["id"], finalize=True)
        return result["next_round"]

    # 사용자

    def test_save_and_load_user(self):
        self.assertIsNone(session.saved_user())
        session.save_user("abc-1_x")
        self.assertEqual(session.saved_user(), "abc-1_x")
        self.assertTrue(os.path.isdir(os.path.join(study.SUBMISSIONS_DIR, "abc-1_x")))
        for bad in ("", "한글", "a b", "../x", "-x"):
            with self.assertRaises(session.SessionError):
                session.save_user(bad)

    # 회차 만들기

    def test_first_run_creates_diagnostic_once(self):
        rnd, created = self.sess.ensure_round()
        self.assertTrue(created)
        self.assertEqual((rnd["id"], rnd["kind"]), ("d1", "diag"))
        again, created = self.sess.ensure_round()
        self.assertFalse(created)
        self.assertEqual(again["id"], "d1")
        for name in ("README.md", "quiz.py"):
            self.assertTrue(os.path.isfile(os.path.join(self.sess.folder("d1"), name)))
        self.assertEqual(len(session.Session("tester").prof["rounds"]), 1)  # 디스크에 저장됨

    def test_round_view_has_everything_the_screen_needs(self):
        rid = self.first_real_round()
        view = self.sess.open_round(rid)
        self.assertEqual(view["kind"], "round")
        kinds = {it["kind"] for it in view["items"]}
        self.assertEqual(kinds, {"quiz", "code"})
        for it in view["items"]:
            self.assertTrue(it["body_md"].strip())
            self.assertFalse(it["answered"])
            self.assertIsNone(it["result"])
            if it["type"] == "choice":
                self.assertGreaterEqual(it["choices"], 4)
                self.assertIn("multi", it)
            if it["kind"] == "code":
                self.assertEqual(it["answer"], it["starter"])
        self.assertEqual([it["no"] for it in view["items"]], list(range(1, len(view["items"]) + 1)))

    # 답 저장

    def test_quiz_answers_round_trip_and_stay_cli_compatible(self):
        rnd, _ = self.sess.ensure_round()
        views = {v["type"]: v for v in self.sess.open_round("d1")["items"]}
        tricky = ['한 줄', "여러\n줄\n출력", 'He said "hi"', "작은'따옴표", "역슬래시 \\n 그대로", '"""삼중"""\n둘째 줄', "  앞뒤 공백 유지  x"]
        target = views.get("output") or views["short"]
        for text in tricky:
            self.sess.set_answer("d1", target["id"], text)
            parsed, error = study.parse_quiz_answers(os.path.join(self.sess.folder("d1"), "quiz.py"))
            self.assertIsNone(error, text)
            self.assertEqual(study.norm_out(str(parsed[target["id"]]), True), study.norm_out(text.strip() if target["type"] == "short" else text, True))
        choice = views["choice"]
        for value, stored in ((3, 3), ([2], 2), ([3, 1], [1, 3]), ([], None), (None, None)):
            self.sess.set_answer("d1", choice["id"], value)
            reopened = {v["id"]: v for v in self.sess.open_round("d1")["items"]}[choice["id"]]
            self.assertEqual(reopened["answer"], stored)
            self.assertEqual(reopened["answered"], stored is not None)
        # 다른 문항의 답이 지워지지 않음
        self.sess.set_answer("d1", target["id"], "남아 있어야 함")
        self.sess.set_answer("d1", choice["id"], 1)
        answers = {v["id"]: v["answer"] for v in self.sess.open_round("d1")["items"]}
        self.assertEqual((answers[target["id"]], answers[choice["id"]]), ("남아 있어야 함", 1))

    def test_literal_is_always_a_valid_python_literal(self):
        for value in (None, 3, [1, 3], "", "a", "a\nb", 'q"q', "t'''t", '"""\n', "back\\slash\nline", "끝이 따옴표\"\n둘째"):
            self.assertEqual(study.norm_out(str(ast.literal_eval(session.literal(value))), True) if isinstance(value, str) else ast.literal_eval(session.literal(value)),
                             study.norm_out(value, True) if isinstance(value, str) else value)

    def test_code_answer_saved_and_reset(self):
        rid = self.first_real_round()
        code = next(v for v in self.sess.open_round(rid)["items"] if v["kind"] == "code")
        self.sess.set_answer(rid, code["id"], "x = 1\r\nprint(x)")
        path = os.path.join(self.sess.folder(rid), code["id"] + ".py")
        self.assertEqual(study.read_text(path), "x = 1\nprint(x)\n")
        self.assertTrue({v["id"]: v for v in self.sess.open_round(rid)["items"]}[code["id"]]["answered"])
        self.assertEqual(self.sess.reset_item(rid, code["id"]), code["starter"])
        self.assertFalse({v["id"]: v for v in self.sess.open_round(rid)["items"]}[code["id"]]["answered"])
        self.assertEqual([f for f in os.listdir(self.sess.folder(rid)) if ".tmp" in f], [])  # 임시 파일이 남지 않음

    # 코드 실행

    def test_try_run_shows_examples_and_records_nothing(self):
        rid = self.first_real_round()
        before = len(self.sess.prof["attempts"])
        for code in (v for v in self.sess.open_round(rid)["items"] if v["kind"] == "code"):
            self.sess.set_answer(rid, code["id"], right_answer(self.sess, code))
            run = self.sess.try_run(rid, code["id"])
            self.assertEqual(run["message"], "", code["id"])
            self.assertEqual(run["ran"], run["examples"])
            self.assertEqual(run["examples"], self.sess.cat[code["key"]]["spec"]["examples"])
            self.assertTrue(all(c["ok"] and c["want"] and c["input"] for c in run["cases"]), (code["id"], run))
            self.sess.set_answer(rid, code["id"], "def solution(*a):\n    return None\n" if code["type"] == "return" else "print('x')\n")
            bad = self.sess.try_run(rid, code["id"])
            self.assertTrue(bad["message"] or any(not c["ok"] for c in bad["cases"]), code["id"])
        self.assertEqual(len(self.sess.prof["attempts"]), before)
        self.assertIsNone(adaptive.find_round(self.sess.prof, rid).get("results"))

    def test_try_run_reports_syntax_error_and_unfilled_blank(self):
        rid = self.first_real_round()
        items = [v for v in self.sess.open_round(rid)["items"] if v["kind"] == "code"]
        plain = next(v for v in items if v["type"] != "fill")
        self.sess.set_answer(rid, plain["id"], "def broken(:\n")
        self.assertIn("문법 오류", self.sess.try_run(rid, plain["id"])["message"])
        fill = next((v for v in items if v["type"] == "fill"), None)
        if fill:
            self.sess.reset_item(rid, fill["id"])
            self.assertIn("빈칸", self.sess.try_run(rid, fill["id"])["message"])

    # 채점 · 기록

    def test_untouched_round_is_not_recorded(self):
        self.sess.ensure_round()
        result = self.sess.grade("d1")
        self.assertTrue(result["untouched"])
        self.assertEqual(self.sess.prof["attempts"], [])
        self.assertFalse(result["completed"])

    def test_partial_submit_records_only_answered_items(self):
        self.sess.ensure_round()
        self.answer_all("d1", only={1, 2, 3})
        result = self.sess.grade("d1")
        self.assertEqual(len(self.sess.prof["attempts"]), 3)
        self.assertFalse(result["completed"])
        self.assertEqual(result["unanswered"], result["round"]["size"] - 3)
        self.assertIsNone(result["next_round"])
        self.answer_all("d1")  # 나머지를 마저 풀면 그때가 그 문항들의 첫 시도
        result = self.sess.grade("d1")
        self.assertTrue(result["completed_now"])
        self.assertEqual(result["next_round"], "r01")
        firsts = adaptive.first_attempts(self.sess.prof)
        self.assertEqual(len(firsts), result["round"]["size"])
        self.assertTrue(all(a["ok"] for a in firsts))

    def test_finalize_marks_blanks_wrong_and_moves_on(self):
        self.sess.ensure_round()
        self.answer_all("d1", only={1})
        result = self.sess.grade("d1", finalize=True)
        self.assertTrue(result["completed_now"])
        self.assertEqual(result["next_round"], "r01")
        size = result["round"]["size"]
        self.assertEqual(len(self.sess.prof["attempts"]), size)
        self.assertEqual(sum(1 for a in self.sess.prof["attempts"] if a.get("skipped")), size - 1)
        self.assertEqual(sum(1 for a in self.sess.prof["attempts"] if a["ok"]), 1)
        again = self.sess.grade("d1", finalize=True)  # 다시 채점해도 중복 기록 없음
        self.assertEqual(len(self.sess.prof["attempts"]), size)
        self.assertFalse(again["completed_now"])
        self.assertIsNone(again["next_round"])

    def test_first_attempt_is_what_counts_for_mastery(self):
        rid = self.first_real_round()
        self.answer_all(rid, correct=False)
        result = self.sess.grade(rid, finalize=True)
        self.assertEqual(result["earned"], 0)
        size = result["round"]["size"]
        self.answer_all(rid, correct=True)  # 고쳐서 다시 채점 = 연습
        result = self.sess.grade(rid)
        self.assertEqual(result["earned"], result["total"])
        in_round = [a for a in self.sess.prof["attempts"] if a["round"] == rid]
        self.assertEqual(sum(1 for a in in_round if a["try"] == 1 and not a["ok"]), size)
        self.assertEqual(sum(1 for a in in_round if a["try"] == 2 and a["ok"]), size)
        self.assertEqual(len(adaptive.first_attempts(self.sess.prof)), len(self.sess.prof["attempts"]) - size)

    def test_all_correct_round_scores_full_and_gui_files_match_ci_grading(self):
        rid = self.first_real_round()
        self.answer_all(rid)
        result = self.sess.grade(rid, finalize=True)
        self.assertEqual((result["earned"], result["ratio"]), (result["total"], 1.0))
        self.assertTrue(result["verdicts"])
        self.assertTrue(all(it["state"] == "ok" for it in result["items"]))
        # CI 가 쓰는 경로(파일만 보고 채점)로도 같은 결과
        fresh = session.Session("tester")
        rnd = adaptive.find_round(fresh.prof, rid)
        self.assertTrue(all(it["state"] == "ok" for it in adaptive.grade_round("tester", rnd, fresh.cat)))
        self.assertEqual(fresh.prof["rounds"][-1]["id"], result["next_round"])

    # 해설

    def test_explain_is_locked_until_graded(self):
        self.sess.ensure_round()
        first = self.sess.open_round("d1")["items"][0]
        with self.assertRaises(session.SessionError):
            self.sess.explain("d1", first["id"])
        self.answer_all("d1", only={1})
        self.sess.grade("d1")  # 일부만 채점한 상태에서는 그 문항 해설도 잠겨 있음
        with self.assertRaises(session.SessionError):
            self.sess.explain("d1", first["id"])
        self.sess.grade("d1", finalize=True)
        info = self.sess.explain("d1", first["id"])
        self.assertTrue(info["answer"] and info["explain"])
        self.assertFalse(info["markdown"])
        rid = self.sess.latest()["id"]
        code = next(v for v in self.sess.open_round(rid)["items"] if v["kind"] == "code")
        with self.assertRaises(session.SessionError):
            self.sess.explain(rid, code["id"])
        self.sess.grade(rid, finalize=True)
        info = self.sess.explain(rid, code["id"])
        self.assertTrue(info["solution"] and info["markdown"])

    # 현황

    def test_overview_tracks_progress(self):
        before = self.sess.overview()
        self.assertEqual((before["readiness"], before["current"], before["rounds"]), (0, None, []))
        self.sess.ensure_round()
        self.answer_all("d1")
        self.sess.grade("d1")
        after = self.sess.overview()
        self.assertGreater(after["readiness"], 0)
        self.assertEqual(after["current"]["id"], "r01")
        self.assertEqual(len(after["units"]), len(adaptive.units()))
        self.assertTrue(all(u["tested"] for u in after["units"]))
        self.assertEqual([r["id"] for r in after["rounds"]], ["d1", "r01"])

    # 기록을 망가뜨리던 경로들

    def test_broken_answer_sheet_is_never_treated_as_empty(self):
        self.sess.ensure_round()
        views = self.sess.open_round("d1")["items"]
        for view in [v for v in views if v["type"] == "choice"][:4]:
            self.sess.set_answer("d1", view["id"], 1)
        path = os.path.join(self.sess.folder("d1"), "quiz.py")
        good = study.read_text(path)
        one_bad_line = good.replace(" = 1 ", " = 1번 ", 1)
        for broken in (one_bad_line, "<<<<<<< HEAD\n" + good + "=======\n>>>>>>> main\n", good + 'x = """끝나지 않은 문자열\n'):
            study.write_text(path, broken)
            self.assertTrue(self.sess.quiz_problem("d1"))
            for call in (lambda: self.sess.open_round("d1"), lambda: self.sess.set_answer("d1", views[5]["id"], 1),
                         lambda: self.sess.grade("d1"), lambda: self.sess.grade("d1", finalize=True)):
                with self.assertRaises(session.SessionError):
                    call()
            self.assertEqual(study.read_text(path), broken)  # 파일을 건드리지 않음
            self.assertEqual(self.sess.prof["attempts"], [])  # 아무것도 기록하지 않음
        study.write_text(path, one_bad_line)
        kept = self.sess.repair_quiz("d1")
        self.assertEqual(kept, 3)  # 깨진 한 줄만 잃음
        self.assertTrue(os.path.isfile(path + ".bak"))
        self.assertIsNone(self.sess.quiz_problem("d1"))
        self.assertEqual(sum(1 for v in self.sess.open_round("d1")["items"] if v["answered"]), 3)

    def test_unsafe_characters_never_reach_the_files(self):
        rid = self.first_real_round()
        views = self.sess.open_round(rid)["items"]
        text_item = next(v for v in views if v["type"] in ("output", "short"))
        code = next(v for v in views if v["kind"] == "code")
        self.sess.set_answer(rid, text_item["id"], "a\x00b\ud83dc\r\nd")
        self.sess.set_answer(rid, code["id"], "x = 1\x00\ud800\n")
        reopened = {v["id"]: v for v in self.sess.open_round(rid)["items"]}
        self.assertEqual(reopened[text_item["id"]]["answer"].replace("\n", " "), "abc d")
        self.assertEqual(reopened[code["id"]]["answer"], "x = 1\n")

    def test_regrading_does_not_change_the_score_used_for_next_round_size(self):
        rid = self.first_real_round()
        self.answer_all(rid, correct=False)
        self.sess.grade(rid, finalize=True)
        rnd = adaptive.find_round(self.sess.prof, rid)
        first, ratio = rnd["first_score"], adaptive.last_ratio(self.sess.prof)
        self.assertEqual(ratio, 0.0)
        self.answer_all(rid, correct=True)
        result = self.sess.grade(rid)
        self.assertEqual(result["earned"], result["total"])
        rnd = adaptive.find_round(self.sess.prof, rid)
        self.assertEqual(rnd["first_score"], first)
        self.assertNotEqual(rnd["score"], first)
        ordered = [r for r in self.sess.prof["rounds"] if r.get("completed_at")]
        self.assertEqual(ordered[-1]["id"], rid)
        self.assertEqual(adaptive.last_ratio(self.sess.prof), 0.0)

    def test_two_sessions_do_not_overwrite_each_others_first_attempts(self):
        self.sess.ensure_round()
        other = session.Session("tester")  # 다른 창(또는 터미널)
        first = self.sess.open_round("d1")["items"][0]
        other.set_answer("d1", first["id"], wrong_answer(first))
        other.grade("d1")  # 오답이 첫 시도로 기록됨
        self.sess.set_answer("d1", first["id"], right_answer(self.sess, first))
        self.sess.grade("d1")  # 앞서 열어 둔 세션이 고쳐서 채점
        attempts = [a for a in session.Session("tester").prof["attempts"] if a["item"] == first["key"]]
        self.assertEqual([(a["try"], a["ok"]) for a in attempts], [(1, False), (2, True)])

    def test_corrupt_profile_raises_readable_error(self):
        self.sess.ensure_round()
        study.write_text(adaptive.profile_path("tester"), '{"user": "tester", "rounds": [<<<<<<<')
        with self.assertRaises(session.SessionError):
            session.Session("tester")
        with self.assertRaises(session.SessionError):
            self.sess.grade("d1", finalize=True)

    def test_choice_buttons_match_the_real_options_for_every_question(self):
        for key, it in self.sess.cat.items():
            if it["kind"] == "quiz" and it["type"] == "choice":
                count = session.choice_count(adaptive.quiz_section(it["set"], it["q"]["id"]))
                self.assertGreaterEqual(count, max(it["q"]["answer"]), key)
                self.assertIn(count, (4, 5), key)
        for key in ("s09/Q3", "s10/Q2", "s04/Q5"):  # 보기가 코드 블록인 문항
            it = self.sess.cat[key]
            self.assertEqual(session.choice_count(adaptive.quiz_section(it["set"], it["q"]["id"])), 4, key)

    def test_try_run_shows_prints_made_inside_a_function(self):
        spec = next(it["spec"] for it in self.sess.cat.values() if it["kind"] == "code" and it["spec"]["mode"] == "call")
        path = os.path.join(self.tmp, "sol.py")
        study.write_text(path, "def solution(*args, **kw):\n    print('디버그', len(args))\n    return None\n")
        run = study.run_cases(spec, path, limit=1)
        self.assertIn("디버그", run["cases"][0]["printed"])
        self.assertFalse(run["cases"][0]["ok"])

    def test_write_text_cleans_up_when_replace_fails(self):
        target = os.path.join(self.tmp, "locked.txt")
        study.write_text(target, "원래 내용")
        real = os.replace

        def always_locked(src, dst):
            raise PermissionError("잠김")

        os.replace = always_locked
        try:
            with self.assertRaises(PermissionError):
                study.write_text(target, "새 내용")
        finally:
            os.replace = real
        self.assertEqual(study.read_text(target), "원래 내용")
        self.assertEqual(os.listdir(self.tmp).count("locked.txt"), 1)
        self.assertEqual([f for f in os.listdir(self.tmp) if ".tmp" in f], [])

    def test_unknown_round_or_item_raises_readable_error(self):
        self.sess.ensure_round()
        for call in (lambda: self.sess.open_round("r99"), lambda: self.sess.set_answer("d1", "nope", 1),
                     lambda: self.sess.try_run("d1", self.sess.open_round("d1")["items"][0]["id"])):
            with self.assertRaises(session.SessionError):
                call()


if __name__ == "__main__":
    unittest.main()
