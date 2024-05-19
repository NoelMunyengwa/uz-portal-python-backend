import random
from flask import Flask, request, jsonify
import json
app = Flask(__name__)

#GET dummy data
@app.route('/get_data', methods=['GET'])
def get_data():
    print("CALLED BY LARAVEL APP")
    return jsonify({"courses": ["Math", "Science", "English", "History", "Geography", "Physics", "Chemistry", "Biology"] });

@app.route('/genetic_timetable', methods=['POST'])
def generate_timetable():
    # Get the request data
    data = request.get_json()
    # print(data) # [{"courses":"HCT416","durations":"2","lecturers":"Mr Aldrin"},{"courses":"HCT420","durations":"1","lecturers":"Miss Jowa"}]
    # print("CALLED BY LARAVEL APP")

    # Extract the venues, course names, durations, and lecturers from the request data
    venues = ["Room 1", "Room 2", "Room 3", "Room 4"]
    courses = []
    durations = []
    lecturers = []
    # convert data to a list
    data = json.loads(data)
    #print data length
    # print(len(data))
    # print("looping through data")
    # Extract the courses, durations, and lecturers from the request data
    for course in data:
        # print(course)
        courses.append(course["courses"])
        durations.append(int(course["durations"]))
        lecturers.append(course["lecturers"])

    # ... rest of the code ...
    # app.run()
# Define the available time slots
    time_slots = [
        ["8:00-9:00", "8:00-10:00"],
        ["9:00-10:00", "9:00-11:00"],
        ["10:00-11:00", "10:00-12:00"],
        ["11:00-12:00", "11:00-1:00"],
        ["12:00-1:00", "12:00-2:00"],
        ["2:00-3:00", "2:00-4:00"],
        ["3:00-4:00", "3:00-5:00"]
    ]

    # Define the courses, venues, durations, and lecturers
    # courses = ["Math", "Science", "English", "History", "Geography", "Physics", "Chemistry", "Biology"]
    # venues = ["Room 1", "Room 2", "Room 3", "Room 4"]
    # durations = [1, 2, 1, 2, 1, 2, 1, 2]  # in hours
    # lecturers = ["Lecturer 1", "Lecturer 2", "Lecturer 3", "Lecturer 4"]
    lecturer_courses = {
        "Mr Aldrin": ["HCT416"],
        "Miss Jowa": ["HCT420"],
        "Mr Munyaradzi": ["HCT402"],
       
    }
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Define the population size and mutation rate
    POP_SIZE = 100
    MUT_RATE = 0.1

    # Define the fitness function
    def fitness(timetable):
        day_courses = {day: 0 for day in days}
        for course in timetable:
            day_courses[course[3]] += 1  # increment course count for the day
        return 1 / (max(day_courses.values()) - min(day_courses.values()) + 1)  # higher fitness for more even distribution

    # Define the genetic algorithm
    def genetic_algorithm():
        # Initialize population
        population = []
        for _ in range(POP_SIZE):
            timetable = []
            for i in range(len(courses)):
                course = courses[i]
                venue = random.choice(venues)
                day = random.choice(days)
                duration = durations[i]
                time_slot_index = i % len(time_slots)  # reuse time slots if necessary
                time_slot_options = time_slots[time_slot_index]
                time_slot = random.choice(time_slot_options)
                if duration == 2:
                    time_slot = time_slot_options[1]  # select the 2-hour time slot
                lecturer = random.choice(list(lecturer_courses.keys()))
                while course not in lecturer_courses[lecturer]:
                    lecturer = random.choice(list(lecturer_courses.keys()))
                timetable.append([course, venue, time_slot, day, duration, lecturer])
            population.append(timetable)

        # Evolve population
        for _ in range(100):  # generations
            # Evaluate fitness
            fitnesses = [fitness(timetable) for timetable in population]
            # Select parents
            parents = random.choices(population, weights=fitnesses, k=POP_SIZE)
            # Crossover
            offspring = []
            for _ in range(POP_SIZE):
                parent1, parent2 = random.sample(parents, 2)
                child = parent1[:2] + parent2[2:]  # crossover
                offspring.append(child)
            # Mutate
            for timetable in offspring:
                if random.random() < MUT_RATE:
                    i = random.randint(0, len(timetable)-1)
                    timetable[i][3] = random.choice(days)  # mutate day
            # Replace population
            population = offspring

        # Return the fittest timetable
        return max(population, key=fitness)

    # Run the genetic algorithm
    timetable = genetic_algorithm()
    print("Timetable:" + str(timetable))

    return jsonify({"timetable": timetable})

# Print the generated timetable
# print("Timetable:")
# for entry in timetable:
#     print(f"Course: {entry[0]}, Venue: {entry[1]}, Time: {entry[2]}, Day: {entry[3]}, Duration: {entry[4]} hours, Lecturer: {entry[5]}")

# # Check for time clashes
# for i in range(len(timetable)):
#     for j in range(i+1, len(timetable)):
#         if (timetable[i][2] == timetable[j][2] and  # same time slot
#             timetable[i][3] == timetable[j][3] and  # same day
#             timetable[i][5] == timetable[j][5]):
#             print(f"Time clash between {timetable[i][0]} and {timetable[j][0]}")
# Output: