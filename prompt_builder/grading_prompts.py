def build_open_test_prompt(subject, num_questions, solution_text, expected_average, student_texts):
    prompt = f"""
You are an intelligent and objective exam grader. The exam type is: OPEN QUESTIONS.

Subject: {subject}
Number of questions: {num_questions}

Reference solution:
{solution_text if solution_text else '[NO SOLUTION GIVEN — use your own knowledge]'}

Grade the following student exams. Each answer should be graded from 0 to 100.
Adjust grading (if needed) so that the average score is approximately (10%) {expected_average if expected_average else 'natural'}.

Return for each student:
[{{
  "student": "filename",
  "grades": [{{ "question_number": int, "grade": int }}],
  "overall_score": grade
}}]
Only output valid JSON format.
"""

    student_blocks = "\n".join([
        f"STUDENT: {filename}\n{text}" for filename, text in student_texts
    ])

    return prompt + "\n\n" + student_blocks


def build_multichoice_prompt(subject, num_questions, solution_text, expected_average, student_texts):
    prompt = f"""
You are a strict grader for multiple choice exams.

Subject: {subject}
Number of questions: {num_questions}

Correct answers:
{solution_text if solution_text else '[NO ANSWER KEY PROVIDED — use best guess]'}

Each question is worth 100 / num_questions points. Mark answers as correct (1) or incorrect (0).
Adjust the scores to target an average of (10%) {expected_average if expected_average else 'natural'}.

Return for each student:
[{{
  "student": "filename",
  "grades": [{{ "question_number": int, "grade": int }}],
  "overall_score": grade
}}]
Only output valid JSON format.
"""

    student_blocks = "\n".join([
        f"STUDENT: {filename}\n{text}" for filename, text in student_texts
    ])

    return prompt + "\n\n" + student_blocks


def build_homework_prompt(subject, num_questions, solution_text, expected_average, student_texts):
    prompt = f"""
You are a fair grader for homework assignments.

Subject: {subject}
Number of questions: {num_questions}

Reference solution:
{solution_text if solution_text else '[NO SOLUTION GIVEN — use your own knowledge]'}

Each question should be graded fairly, but with less strictness than in exams.
Adjust grades to have a target average of (10%) {expected_average if expected_average else 'natural'}.

Return for each student:
[{{
  "student": "filename",
  "grades": [{{ "question_number": int, "grade": int }}],
  "overall_score": grade
}}]
Only output valid JSON format.
"""

    student_blocks = "\n".join([
        f"STUDENT: {filename}\n{text}" for filename, text in student_texts
    ])

    return prompt + "\n\n" + student_blocks
