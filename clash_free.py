import random
from flask import Flask, request, jsonify
import json
from flask_mysqldb import MySQL
app = Flask(__name__)
app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_PORT']=3306
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='adminPortal'

mysql = MySQL(app)
#GET dummy data
@app.route('/get_data', methods=['GET'])
def get_data():
    print("CALLED BY LARAVEL APP")
    return jsonify({"courses": ["Math", "Science", "English", "History", "Geography", "Physics", "Chemistry", "Biology"] });

@app.route('/genetic_timetable', methods=['POST'])
def generate_timetable():
    # Get the request data
    data = request.get_json()

    # Extract the venues, course names, durations, and lecturers from the request data
    venues = ["SLT500", "SW-Lab", "HW-Lab", "Maths LT","CS Basement", "Room 6","Room 7", "Room 8"]
    courses = []
    durations = []
    lecturers = []
    # convert data to a list
    data = json.loads(data)
    print(data)
    # print("looping through data")
    # Extract the courses, durations, and lecturers from the request data
    for course in data:
        # print(course)
        courses.append(course["courses"])
        durations.append(int(course["durations"]))
        lecturers.append(course["lecturers"])

    


# available time slots
    time_slots = [
        ["8:00-9:00", "8:00-10:00"],
        ["9:00-10:00", "9:00-11:00"],
        ["10:00-11:00", "10:00-12:00"],
        ["11:00-12:00", "11:00-1:00"],
        ["12:00-1:00", "12:00-2:00"],
        ["2:00-3:00", "2:00-4:00"],
        ["3:00-4:00", "3:00-5:00"]
    ]

    # Group courses by lecturer
    lecturer_courses = {}
    for course in data:
        lecturer = course["lecturers"]
        course_name = course["courses"]
        if lecturer in lecturer_courses:
            lecturer_courses[lecturer].append(course_name)
        else:
            lecturer_courses[lecturer] = [course_name]
       
    
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
    
    # Fetch isCompassWide and isRepeated courses from the database
    cur = mysql.connection.cursor()
    isCompassWide = []
    cur.execute("SELECT course_code FROM timetables WHERE isCampusWide = 'On'")
    isCompassWide = [row[0] for row in cur.fetchall()]
    print("isCompassWide: ", isCompassWide)

    cur.execute("SELECT course_code FROM timetables WHERE isRepeated = 'On'")
    isRepeated = [row[0] for row in cur.fetchall()]
    cur.close()

    # Define the genetic algorithm
    def genetic_algorithm():
        # Initialize population
        population = []
        for _ in range(POP_SIZE):
            timetable = []
            for i in range(len(courses)):
                course = courses[i]
                if course in isCompassWide or course in isRepeated:
                    # Use existing day, venue, and time from the database
                    print("Using existing day, venue, and time from the database")
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT venue, time,day,duration, lecturer FROM timetables WHERE course_code = %s", (course,))
                    row = cur.fetchone()
                    cur.close()
                    print("Row: ", row)
                    venue, time_slot,day,duration, lecturer = row
                else:
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

    # # Define the genetic algorithm
    # def genetic_algorithm():
    #     # Initialize population
        
    #     population = []
    #     for _ in range(POP_SIZE):
    #         timetable = []
            
    #         for i in range(len(courses)):
    #             course = courses[i]
    #             venue = random.choice(venues)
    #             day = random.choice(days)
    #             duration = durations[i]
    #             time_slot_index = i % len(time_slots)  # reuse time slots if necessary
    #             time_slot_options = time_slots[time_slot_index]
    #             time_slot = random.choice(time_slot_options)
    #             if duration == 2:
    #                 time_slot = time_slot_options[1]  # select the 2-hour time slot
    #             lecturer = random.choice(list(lecturer_courses.keys()))
                
    #             while course not in lecturer_courses[lecturer] :
    #                 lecturer = random.choice(list(lecturer_courses.keys()))
    #             timetable.append([course, venue, time_slot, day, duration, lecturer])
    #         population.append(timetable)

        # Evolve population
        print("Evolving population")
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
                    course = timetable[i][0]
                    for entry in timetable:
                        if entry[0] in isCompassWide or entry[0] in isRepeated:
                            continue
                        entry[3] = random.choice(days)  # mutate day
            # # Mutate
            # for timetable in offspring:
            #     if random.random() < MUT_RATE:
            #         i = random.randint(0, len(timetable)-1)
            #         timetable[i][3] = random.choice(days)  # mutate day
            # Replace population
            population = offspring

        # Return the fittest timetable
        return max(population, key=fitness)

    # Run the genetic algorithm
    
    timetable = genetic_algorithm()
    print("Timetable:" + str(timetable))
    #Call the Ant colony algorithm
    #loop and insert timetable into database called timetables
    for entry in timetable:
        print("Inserting into database")
        cur = mysql.connection.cursor()
        #get department and level from database using the course code in the entry
        cur.execute("SELECT department, level, isCampusWide FROM courses WHERE course_code = %s", (entry[0],))
        row = cur.fetchone()
        dep = row[0]
        levl = row[1]
        isCampusWide = row[2]

        cur.execute("INSERT INTO timetables (department,level,course_code, venue, time, day, duration, lecturer,isCampusWide) VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s)", (dep,levl,entry[0], entry[1], entry[2], entry[3], entry[4], entry[5],isCampusWide))
        mysql.connection.commit()
        cur.close()


    return jsonify({"timetable": timetable})

