#2020510027, Tuğrul Demirözer
#2020510005, Mustafa Can Akıncı

import json
import csv
import operator

operators = { #Dictionary where operators and their operations match
    '-': operator.sub,
    '+': operator.add,
    '=': operator.eq,
    '|=': operator.ior,
    '!=': operator.ne,
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '!<': operator.ge,
    '!>': operator.le,
    'AND': operator.and_,
    'OR': operator.or_
}
def main():
    students = read_CSV() #Read CSV file and return a dictionary
    statement : str = input("Enter a statement: ") #takes command from user
    match = match_sql_statement(statement, students) #Match the SQL statement and return the result
def match_sql_statement(sql_statement, students): 
    #Calling the select_operation() function if the #SQL statement contains SELECT and FROM
    if "SELECT" in sql_statement and "FROM" in sql_statement:
        subDict = select_operation(sql_statement, students)
        write_JSON(subDict)  
    #Calling the insert_operation() function if the SQL statement contains INSERT INTO and VALUES 
    elif "INSERT" in sql_statement and "INTO" in sql_statement and "VALUES" in sql_statement:
        students = insert_operation(sql_statement, students)
        write_JSON(students)
    #Calling the delete operation() function if the SQL statement contains DELETE FROM
    elif "DELETE" in sql_statement and "FROM" in sql_statement:
        students = delete_operation(sql_statement, students)
        write_JSON(students)
    else:
        raise Exception("Invalid SQL statement")
def insert_operation(sql_statement, students):
    start_index = sql_statement.find("VALUES") + 7
    end_index = sql_statement.find(")")
    values = sql_statement[start_index:end_index].strip().split(",")
    validateValues(values)
    id = int(values[0])
    students[id] = { #Validate values
        'name': values[1].strip().strip("'"),
        'lastname': values[2].strip().strip("'"),
        'email': values[3].strip().strip("'"),
        'grade': int(values[4])
    }
    return students
def validateValues(values): #control of values
    if len(values) != 5:
        raise Exception("Invalid number of values")
    if not values[0].isdigit():
        raise Exception("Invalid id")
    if not values[1].replace('‘','\'').replace('’','\'').strip("'").isalpha():
        raise Exception("Invalid name")
    if not values[2].replace('‘','\'').replace('’','\'').strip("'").isalpha():
        raise Exception("Invalid lastname")
    if not values[3].count('@') == 1 or not values[3].count('.') >= 1:
        raise Exception("Invalid email")
    if not values[4].isdigit():
        raise Exception("Invalid grade")
def delete_operation(sql_statement, students):
    condition = sql_statement[sql_statement.find("WHERE")+5:].strip().split(" ")
    if len(condition) == 7:
        first_id_list = [int(i) for i in take_subDict(students, condition[:3], condition[0].lower()).keys()] #Retrieves student ID lists for two subsets
        second_id_list = [int(i) for i in take_subDict(students, condition[4:], condition[4].lower()).keys()]
        id_list = list(set(first_id_list) & set(second_id_list)) #Determines the student IDs to be deleted by taking the intersection of two subsets
    elif len(condition) == 3: #Retrieves student IDs for a single subset
        id_list = [int(i) for i in take_subDict(students, condition, condition[0].lower()).keys()]
    
    for id in id_list: #Deletes the determined student records from the data
        del students[id]

    return students
def write_JSON(subDict): #Writes subDict to 'result.json'
    with open('result.json', 'w') as fp:
        json.dump(subDict, fp, indent=4)    
def select_operation(sql_statement, students):
    columns = extract_columns(sql_statement) #strips columns and spaces
    condition = extract_condition(sql_statement).split(" ")
    if len(condition) == 7: 
        #Retrieves student records for two subsets
        first_subDict = take_subDict(students, condition[:3], condition[0].lower(),columns)
        second_subDict = take_subDict(students, condition[4:], condition[4].lower(),columns)
        subDict = {k: v for k, v in first_subDict.items() if k in second_subDict} #Retrieves student records at the intersection of two subsets
    elif len(condition) == 3: #Retrieves student records in a single subset
        subDict = take_subDict(students, condition, condition[0].lower(),columns)    
        
    order =  sql_statement[sql_statement.find("BY")+3:].strip() == "DSC" #Does the sorting
    subDict = sorted(subDict.items(), key=lambda x: int(x[0]), reverse=order)
    return subDict
def take_subDict(students, condition, parameter,columns): #Selects a subset of student records based on the given condition
    subDict = {}
    for student in students:
        a = students[student][parameter]
        typeA = type(a)
        b = typeA(condition[2])
        operation = operators[condition[1]]
        if typeA == str: 
            a = a.lower()
            b = b.lower().replace('‘','\'').replace('’','\'').strip("'")
        if operation(a, b): 
            if columns[0] == "*": #Adds student record directly to subset if all columns are selected
                subDict[student] = students[student]
            else: #If specific columns are selected, subset will be taken by taking the relevant columns from the student record
                subDict[student] = {} 
                for column in columns:
                    subDict[student][column] = students[student][column]
    return subDict        
def extract_condition(sql_statement): #Extracts the WHERE part of the SQL statement
    start_index = sql_statement.find("WHERE") + 5
    end_index = sql_statement.find("ORDER")
    condition = sql_statement[start_index:end_index].strip()

    return condition
def extract_columns(sql_statement): #Extracts the SELECT part in the SQL statement
    start_index = sql_statement.find("SELECT") + 6
    end_index = sql_statement.find("FROM")
    columns = sql_statement[start_index:end_index].strip()
    columns = columns.split(",")
    return columns    
def read_CSV(): #Returns students.csv data as a dictionary
    data = {}
    with open("students.csv", 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            key = int(row['id'])
            values = {
                'name': row['name'],
                'lastname': row['lastname'],
                'email': row['email'],
                'grade': int(row['grade'])
            }
            data[key] = values
    return dict(sorted(data.items(), key=lambda x: int(x[0])))
if __name__ == "__main__":
    main()
