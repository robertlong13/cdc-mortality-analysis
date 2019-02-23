# Parent class for each field on a line. The contructor takes one line from
# the CDC mortality datafile and stores the code for that field as a string.
# A human readable version of that code can be obtained by using the str()
# funtion, or it can be passed straight to the print() function
#
# Derived classes must define the start/end characters for where to find the
# code on each line. Then, they should define a dictionary, printable_strings,
# that converts the code into a readable string. More complicated fields
# will need to override the __str__() method.
#
# Only a handful of the fields are defined in this file, if you want to add
# another one, the record layout document can be found on the same page you
# download the datafile.
class Field():
    def __init__(self, line):
        self.code = line[self._rec_start-1:self._rec_end]
        
    def __str__(self):
        return self.printable_strings[self.code]
        
class MonthOfDeath(Field):
    _rec_start = 65
    _rec_end = 66
    printable_strings = {'01':'January',
                         '02':'February',
                         '03':'March',
                         '04':'April',
                         '05':'May',
                         '06':'June',
                         '07':'July',
                         '08':'August',
                         '09':'September',
                         '10':'October',
                         '11':'November',
                         '12':'December'}
                         
class DayOfWeekOfDeath(Field):
    _rec_start = 85
    _rec_end = 85
    printable_strings = {'1':'Sunday',
                         '2':'Monday',
                         '3':'Tuesday',
                         '4':'Wednesday',
                         '5':'Thursday',
                         '6':'Friday',
                         '7':'Saturday',
                         '9':'UNKNOWN'}
                         
class Sex(Field):
    _rec_start = 69
    _rec_end = 69
    printable_strings = {'M':'Male', 'F':'Female'}
    
class DetailAge(Field):
    _rec_start = 70
    _rec_end = 73
        
    def __str__(self):
        if(self.code[0] == '1'):
            return str(int(self.code[1:])) + ' years'
        elif(self.code[0] == '2'):
            return str(int(self.code[1:])) + ' months'
        elif(self.code[0] == '4'):
            return str(int(self.code[1:])) + ' days'
        elif(self.code[0] == '5'):
            return str(int(self.code[1:])) + ' hours'
        elif(self.code[0] == '6'):
            return str(int(self.code[1:])) + ' minutes'
        elif(self.code[0] == '9'):
            return 'Age not stated'
            
    # Return age in integer years
    def years(self):
        if(self.code[0] == '1'):
            return int(self.code[1:])
        else:
            return 0
    
    # Return age in integer months
    def months(self):
        if(self.code[0] == '1'):
            return 12*int(self.code[1:])
        elif(self.code[0] == '2'):
            return int(self.code[1:])
        else:
            return 0

class AgeRecode12(Field):
    _rec_start = 79
    _rec_end = 80
    printable_strings = {'01':'Under 1 year',
                         '02':'1 - 4 years',
                         '03':'5 - 14 years',
                         '04':'15 - 24 years',
                         '05':'25 - 34 years',
                         '06':'35 - 44 years',
                         '07':'45 - 54 years',
                         '08':'55 - 64 years',
                         '09':'65 - 74 years',
                         '10':'75 - 84 years',
                         '11':'85 years and over',
                         '12':'Age not stated'}
            
class MannerOfDeath(Field):
    _rec_start = 107
    _rec_end = 107
    printable_strings = {'1':'Accident',
                         '2':'Suicide',
                         '3':'Homicide',
                         '4':'Pending investigation',
                         '5':'Could not determine',
                         '6':'Self-Inflicted',
                         '7':'Natural',
                         ' ':'Not specified'}
  
class ICD10Code(Field):
    _rec_start = 146
    _rec_end = 149
    def __str__(self):
        s = self.code[0:3]
        if self.code[3] != ' ':
            s += '.' + self.code[3]
        
        return s

class Race(Field):
    _rec_start = 445
    _rec_end = 446
    printable_strings = {'01':'White',
                         '02':'Black',
                         '03':'American Indian',
                         '04':'Chinese',
                         '05':'Japanese',
                         '06':'Hawaiian',
                         '07':'Filipino',
                         '18':'Asian Indian',
                         '28':'Korean',
                         '38':'Samoan',
                         '48':'Vietnames',
                         '58':'Guamanian',
                         '68':'Other Asian',
                         '78':'Other Asian'}
    
        
if __name__ == '__main__':
    #### Print the leading causes of death for an age range, in years ####
    ageRange = [5, 9]
    # Dictionary containing death counts with manner-of-death as the key
    distribution = {}
    with open('VS17MORT.DUSMCPUB') as fin:
        for line in fin:
            age = DetailAge(line).years()
            if age < ageRange[0] or age > ageRange[1]:
                continue
    
            manner = str(MannerOfDeath(line))
            
            if manner in distribution:
                distribution[manner] += 1
            else:
                distribution[manner] = 1
        
    print('Leading manners of death for', ageRange[0], 'to', ageRange[1],'years')
    leading = sorted(distribution, key=distribution.__getitem__, reverse=True)
    for manner in leading:
        print(manner+':', distribution[manner])
    
    print('\n\n')
    
    #### Print electrocution deaths for the 12 age groups ####
    # We'll use the ICD10 codes to determine if death was by electrocution
    # Codes starting with W85, W86, and W87 denote electrocution
    # https://icd.who.int/browse10/2016/en#/W85
    # W85 - Exposure to electric transmission lines
    # W86 - Exposure to other specified electric current
    # W87 - Exposure to unspecified electric current
    
    # List containing death counts with AgeRecode12 as the key
    distribution = {}
    with open('VS17MORT.DUSMCPUB') as fin:
        for line in fin:    
            icd10code = str(ICD10Code(line))
            icd_val =  float(icd10code[1:])
            if not icd10code.startswith('W') or 85 > icd_val or icd_val >= 88:
                continue
                
            # Use the code as the key to make it easier to sort results by age
            age = AgeRecode12(line).code
            
            if age in distribution:
                distribution[age] += 1
            else:
                distribution[age] = 1
                
        
    print('Electrocution deaths for each age group')
    age_codes = sorted(distribution.keys())
    for code in age_codes:
        print(AgeRecode12.printable_strings[code]+':', distribution[code])
        
        
    #### Export a CSV with just the info you want in it ####
    # As an example, we'll just export the data for ages 1-18, and just the
    # ages, races, and ICD codes
    ageRange = [1, 18]
    with open('VS17MORT.DUSMCPUB') as fin, open('reduced.csv','w') as fout:
        fout.write('AgeYears,Race,ICD10Code\n')
        for line in fin:
            age = DetailAge(line).years()
            if age < ageRange[0] or age > ageRange[1]:
                continue
                
            fout.write(str(age)+','+str(Race(line))+','+str(ICD10Code(line))+'\n')