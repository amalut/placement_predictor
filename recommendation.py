import numpy as np
# Define the recommendation function
def recommend_for_student(student_features, average_values):
    # Make prediction for the new student
    # Initialize recommendations list
    recommendations = []
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
    
    return  recommendations