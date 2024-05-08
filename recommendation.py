import numpy as np
# Define the recommendation function
def recommend_for_student(placement_chance,student_features, average_values):
    # Make prediction for the new student
    # Initialize recommendations list
    recommendations = []
    if placement_chance<0.7:
    # Compare student's attributes with average values and provide recommendations
    # CGPA recommendation
        if student_features[0] < average_values['Cgpa']:
                recommendations.append("Consider improving your CGPA. Try focusing on your academic performance.")
            
            # Communication skills recommendation
        if student_features[1] < average_values['Communication']:
                recommendations.append("Your communication skills seem lower than average. Work on improving your verbal and written communication.")
            
            # Aptitude recommendation
        if student_features[2] < average_values['Aptitude']:
                recommendations.append("Improve your aptitude skills by practicing more reasoning and problem-solving exercises.")
            
            # Internships recommendation
        if student_features[3] < average_values['Internships']:
                recommendations.append("Gaining more internship experience can enhance your profile. Look for internship opportunities.")
    else:
        if placement_chance > 0.99:
            recommendations.extend(["Cognizant", "Qburst"])
        if placement_chance > 0.95:
            recommendations.append("TCS")
        if placement_chance > 0.9:
            recommendations.append("Tata Elexi")
        if placement_chance > 0.85:
            recommendations.extend(["Experion","UST Global"])
        if placement_chance > 0.8:
            recommendations.append("Turbolab")
        if placement_chance >= 0.75:
            recommendations.append("Innovature")
        if placement_chance>=0.7:
             recommendations.append("Keltron")
    
    return  recommendations