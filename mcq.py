from flask import Flask, render_template, request
import random

app = Flask(__name__)

class MultipleChoiceQuestion:
    def __init__(self, question, options, correct_option):
        self.question = question
        self.options = options
        self.correct_option = correct_option

    def display_question(self):
        return f"{self.question}\n" + "\n".join(f"{i}. {option}" for i, option in enumerate(self.options, 1))

    def check_answer(self, user_answer):
        return user_answer == self.correct_option

def run_mcq_quiz(questions):
    score = 0

    for i, question in enumerate(questions, 1):
        question_text = question.display_question()

        try:
            user_answer = int(request.form.get(f"answer_{i}"))
            if 1 <= user_answer <= len(question.options):
                if question.check_answer(user_answer):
                    score += 1
        except (ValueError, TypeError):
            pass

    return score

questions_list = [
    MultipleChoiceQuestion("Six years ago, the ratio of the ages of Kunal and Sagar was 6 : 5. Four years hence, the ratio of their ages will be 11 : 10. What is Sagar's age at present?.", ["16 years", "18 years", "20 years", "22 years"], 1),
    MultipleChoiceQuestion("Two pipes A and B can fill a cistern in 37 minutes and 45 minutes respectively. Both pipes are opened. The cistern will be filled in just half an hour, if the B is turned off after:", ["5 min.", "9 min.", "10 min.", "15 min."], 2),
    MultipleChoiceQuestion("Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?", ["7", "10", "12", "13"], 2),
    MultipleChoiceQuestion("A, B and C can do a piece of work in 20, 30 and 60 days respectively. In how many days can A do the work if he is assisted by B and C on every third day?", ["15", "12", "18", "16"], 1),
    MultipleChoiceQuestion("The angle between the minute hand and the hour hand of a clock when the time is 4.20, is:",["0 degree","20 degree","1 degree","10 degree"], 4),
    MultipleChoiceQuestion("A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?:",["120 meters","324 meteres","180 meteres","150 meters"], 4),
    MultipleChoiceQuestion("A boat can travel with a speed of 13 km/hr in still water. If the speed of the stream is 4 km/hr, find the time taken by the boat to go 68 km downstream?:",["2 hours","3 hours","4 hours","5 hours"], 3),
    MultipleChoiceQuestion("In how many different ways can the letters of the word 'LEADING' be arranged in such a way that the vowels always come together?",["720","360","5040","480"], 1),
    MultipleChoiceQuestion("The true discount on Rs. 1760 due after a certain time at 12% per annum is Rs. 160. The time after which it is due is:",["6 months","10 months","3 months","7 months"], 2),
    MultipleChoiceQuestion("A man has Rs.480 in the denominations of one-rupee notes, five-rupee notes and ten-rupee notes. The number of notes of each denomination is equal. What is the total number of notes that he has ?",["40","60","75","90"], 4),
    MultipleChoiceQuestion("It was Sunday on Jan 1, 2006. What was the day of the week Jan 1, 2010?",["sunday","monday","friday","tuesday"], 3),
    MultipleChoiceQuestion("The percentage increase in the area of a rectangle, if each of its sides is increased by 20% is:",["44%","40%","41%","45%"], 1),
    MultipleChoiceQuestion("Which one of the following is not a prime number?",["71","61","31","91"], 4),
    MultipleChoiceQuestion("What least number must be added to 1056, so that the sum is completely divisible by 23 ?",["3","2","18","21"], 2),
    MultipleChoiceQuestion("A person crosses a 600 m long street in 5 minutes. What is his speed in km per hour?:",["3.6","8.4","7.2","10"], 3),
    MultipleChoiceQuestion("Six bells commence tolling together and toll at intervals of 2, 4, 6, 8 10 and 12 seconds respectively. In 30 minutes, how many times do they toll together ?",["6","16","10","4"], 2),
    MultipleChoiceQuestion("The sum of ages of 5 children born at the intervals of 3 years each is 50 years. What is the age of the youngest child?:",["4 years","8 years","10 years","9 years"], 1),
    MultipleChoiceQuestion("The difference between simple and compound interests compounded annually on a certain sum of money for 2 years at 4% per annum is Re. 1. The sum (in Rs.) is:",["650","640","625","645"], 3),
    MultipleChoiceQuestion("The average of 20 numbers is zero. Of them, at the most, how many may be greater than zero?",["1","0","10","19"], 4),
    MultipleChoiceQuestion("3 pumps, working 8 hours a day, can empty a tank in 2 days. How many hours a day must 4 pumps work to empty the tank in 1 day?",["9","10","12","11"], 3),
    MultipleChoiceQuestion("A can contains a mixture of two liquids A and B is the ratio 7 : 5. When 9 litres of mixture are drawn off and the can is filled with B, the ratio of A and B becomes 7 : 9. How many litres of liquid A was contained by the can initially?:",["21","10","25","20"], 1),
    MultipleChoiceQuestion("The largest 4 digit number exactly divisible by 88 is:",["9768","9944","9988","8888"], 2),
    MultipleChoiceQuestion("How many times are the hands of a clock at right angle in a day?",["24","28","44","48"], 3),
    MultipleChoiceQuestion("A fruit seller had some apples. He sells 40% apples and still has 420 apples. Originally, he had:",["700 apples","800 apples","600 apples","672 apples"], 1),
      MultipleChoiceQuestion("Which of the following is not a leap year?",["800","2000","700","1200"], 3),
]

random.shuffle(questions_list)

if __name__ == '__main__':
    app.run(debug=True)
