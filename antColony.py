from flask import Flask, request, jsonify
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

app = Flask(__name__)

def distance(course1, course2):
    # Modify this function to calculate a distance metric between courses
    # (e.g., consider course prerequisites, similarity in topics)
    return max(np.abs(course1['duration'] - course2['duration']),0.0001)

def ant_colony_optimization(courses, n_ants, n_iterations, alpha, beta, evaporation_rate, Q):
    n_courses = len(courses)
    pheromone = np.ones((n_courses, n_courses))
    best_schedule = None
    best_schedule_duration = np.inf

    for iteration in range(n_iterations):
        schedules = []
        schedule_durations = []

        for ant in range(n_ants):
            visited = [False] * n_courses
            current_course = np.random.randint(n_courses)
            visited[current_course] = True
            schedule = [courses[current_course]]
            schedule_duration = 0

            while False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                probabilities = np.zeros(len(unvisited))

                for i, unvisited_course in enumerate(unvisited):
                    probabilities[i] = pheromone[current_course, unvisited_course] ** alpha / distance(courses[current_course], courses[unvisited_course]) ** beta

                probabilities /= np.sum(probabilities)

                next_course = np.random.choice(unvisited, p=probabilities)
                schedule.append(courses[next_course])
                schedule_duration += courses[next_course]['duration']
                visited[next_course] = True
                current_course = next_course

            schedules.append(schedule)
            schedule_durations.append(schedule_duration)

            if schedule_duration < best_schedule_duration:
                best_schedule = schedule
                best_schedule_duration = schedule_duration

        pheromone *= evaporation_rate

        course_name_to_index = {course['name']: i for i, course in enumerate(courses)}
        for i in range(n_courses - 1):
            current_course_index = course_name_to_index[schedules[i][i]['name']]
            next_course_index = course_name_to_index[schedules[i][i + 1]['name']]
            new_phero = course_name_to_index[schedules[i][-1]['name']]
            old_phero = course_name_to_index[schedules[i][0]['name']]
            pheromone[current_course_index, next_course_index] += Q / schedule_durations[i]

    return best_schedule, best_schedule_duration

@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
  courses = request.get_json()  # Get course data from request body
  n_ants = int(request.args.get('n_ants', 10))  # Get optional query parameter for n_ants
  n_iterations = int(request.args.get('n_iterations', 100))  # Get optional query parameter for n_iterations
  alpha = float(request.args.get('alpha', 1))  # Get optional query parameter for alpha
  beta = float(request.args.get('beta', 1))  # Get optional query parameter for beta
  evaporation_rate = float(request.args.get('evaporation_rate', 0.5))  # Get optional query parameter for evaporation_rate
  Q = float(request.args.get('Q', 1))  # Get optional query parameter for Q

  # Ensure courses each have a 'name' and 'duration' attribute
  if not all(course.get('name') and course.get('duration') for course in courses):
      return jsonify({'error': 'Courses must have "name" and "duration" attributes'}), 400

  best_schedule, best_schedule_duration = ant_colony_optimization(courses, n_ants, n_iterations, alpha, beta, evaporation_rate, Q)

  # Return the timetable as a list of course names
  timetable = [course['name'] for course in best_schedule]
  return jsonify({'timetable': timetable, 'total_duration': best_schedule_duration})

if __name__ == '__main__':
  app.run(debug=True)
