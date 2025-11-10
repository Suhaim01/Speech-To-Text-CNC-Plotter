from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS from flask_cors
from enum import Enum
import os
import math
import argparse

app = Flask(__name__)
CORS(app)  # Apply CORS to your Flask app

class Instr:
    class Type(Enum):
        move = 0,
        write = 1,

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:  # args must be a data str
            attributes = args[0].split(' ')
            self.type = Instr.Type.move if attributes[0][1] == '0' else Instr.Type.write
            self.x = float(attributes[1][1:])
            self.y = float(attributes[2][1:])
        elif len(args) == 3 and type(args[0]) is Instr.Type and type(args[1]) is float and type(args[2]) is float:
            self.type, self.x, self.y = args
        else:
            raise TypeError("Instr() takes one (str) or three (Instr.Type, float, float) arguments")

    def __repr__(self):
        return "G%d X%.2f Y%.2f" % (self.type.value[0], self.x, self.y)

    def translated(self, x, y):
        return Instr(self.type, self.x + x, self.y + y)

class Letter:
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            self.content = args[0]  # Store the content as is
            self.instructions = []  # Initialize instructions as an empty list
            for line in args[0].split('\n'):
                if line.strip() and not line.strip().startswith(('m3', 'm5')):  # Exclude lines starting with 'm3' and 'm5'
                    self.instructions.append(Instr(line))

            pointsOnX = [instr.x for instr in self.instructions]
            self.width = max(pointsOnX) - min(pointsOnX)
        elif len(args) == 2 and type(args[0]) is list and type(args[1]) is float:
            self.instructions = args[0]
            self.width = args[1]
        else:
            raise TypeError("Letter() takes one (str) or two (list, float) arguments")

    def __repr__(self):
        return "\n".join([repr(instr) for instr in self.instructions]) + "\n"

    # def __repr__(self):
        if hasattr(self, 'content'):  # Check if the object has a 'content' attribute
            return self.content  # Return the stored content as the representation
        else:
            return "\n".join([repr(instr) for instr in self.instructions]) + "\n"

    def translated(self, x, y):
        return Letter([instr.translated(x, y) for instr in self.instructions], self.width)


def readLetters(directory):
    letters = {
        " ": Letter([], 4.0),
        "\n": Letter([], math.inf)
    }
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".nc"):  # Check if the file is a Gcode file
                with open(os.path.join(root, filename), "r") as file:
                    letterRepr = file.readline().strip()  # Read the first line and remove any leading/trailing whitespace
                    letter = Letter(file.read())  # Read the remaining content of the file
                    letters[letterRepr] = letter
    return letters

def scale_coordinates(x, y, scale_factor):
    scaled_x = x * scale_factor
    scaled_y = y * scale_factor
    return scaled_x, scaled_y


def rescale_gcode(gcode_lines):
    scaled_gcode = []
    max_x = 0
    max_y = 0
    
    # Calculate the maximum X and Y values
    for line in gcode_lines:
        line_parts = line.strip().split()
        for part in line_parts:
            if part.startswith('X'):
                x_value = abs(float(part[1:]))
                if x_value > max_x:
                    max_x = x_value
            elif part.startswith('Y'):
                y_value = abs(float(part[1:]))
                if y_value > max_y:
                    max_y = y_value
    
    scale_factor = 6 / max(max_x, max_y) if max(max_x, max_y) > 6 else 1  # Calculate scale factor
    
    # Scale and modify each line
    for line in gcode_lines:
        line_parts = line.strip().split()
        if line_parts:  # Check if line_parts is not empty
            new_line = line_parts[0]  # Start with G0 or G1
            x_value = None
            y_value = None
            feedrate_added = False  # Flag to track if feedrate is added
            for part in line_parts[1:]:
                if part.startswith('X'):
                    x_value = float(part[1:])
                elif part.startswith('Y'):
                    y_value = float(part[1:])
                elif part.startswith('F') and not feedrate_added:  # Add feedrate only once
                    new_line += f' F1500'  # Update feedrate
                    feedrate_added = True
            if x_value is not None and y_value is not None:
                scaled_x, scaled_y = scale_coordinates(x_value, y_value, scale_factor)
                new_line += f' X{scaled_x:.2f} Y{scaled_y:.2f}'  # Append scaled coordinates
            scaled_gcode.append(new_line)
        else:
            scaled_gcode.append(line)
    
    return scaled_gcode



# def textToGcode(letters, text, lineLength, lineSpacing, padding):
#     gcodeLettersArray = []
#     offsetX, offsetY = 0, 0
#     first_letter = True  # Track if this is the first letter
#     for char in text:
#         letter = letters[char].translated(offsetX, offsetY)
#         if first_letter:
#             gcodeLettersArray.append('m3 S90')  # Add 'm3 S90' for the first letter
#             gcodeLettersArray.append('m5')  # Add 'm5' for the first letter
#             first_letter = False  # Set first_letter to False after the first letter
#         else:
#             gcodeLettersArray.append('m3')  # Add 'm3' for subsequent letters
#             gcodeLettersArray.append('G0 F1500 X{:0.2f} Y{:0.2f}'.format(offsetX, offsetY))  # Add first G command
#             gcodeLettersArray.append('m5')  # Add 'm5' for subsequent letters
#         lines = repr(letter).split('\n')  # Split the representation by lines
#         for line in lines:
#             if line.strip():  # Check if the line is not empty
#                 if not line.startswith(('m', 'M')):  # Check if the line starts with 'm' or 'M'
#                     line += ' F1500'  # Add ' F1500' to the line
#                 gcodeLettersArray.append(line)
#         offsetX += letter.width + padding
#         if offsetX >= lineLength:
#             offsetX = 0
#             offsetY -= lineSpacing
    
#     # Call the rescale_gcode function to rescale the generated G-code
#     scaled_gcode = rescale_gcode(gcodeLettersArray)
    
#     return "\n".join(scaled_gcode)


# def textToGcode(letters, text, lineLength, lineSpacing, padding):
    gcodeLettersArray = []
    offsetX, offsetY = 0, 0
    for char in text:
        letter = letters[char].translated(offsetX, offsetY)
        gcodeLettersArray.append('m3 S90')  # Add 'm3 S90' before each letter's G-code
        gcodeLettersArray.append('m5')  # Add 'm5' before each letter's G-code
        lines = repr(letter).split('\n')  # Split the representation by lines
        for line in lines:
            if line.strip():  # Check if the line is not empty
                if not line.startswith(('m', 'M')):  # Check if the line starts with 'm' or 'M'
                    line += ' F1500'  # Add ' F1500' to the line
                gcodeLettersArray.append(line)
        offsetX += letter.width + padding
        if offsetX >= lineLength:
            offsetX = 0
            offsetY -= lineSpacing
    
    # Call the rescale_gcode function to rescale the generated G-code
    scaled_gcode = rescale_gcode(gcodeLettersArray)
    


    return "\n".join(scaled_gcode)

def textToGcode(letters, text, lineLength, lineSpacing, padding):
    gcodeLettersArray = ['m3 S90']
    gcodeLettersArray[0]+=' S90'
    offsetX, offsetY = 0, 0
    skipNextLine = False  # Flag to skip the next line after encountering 'm5'
    
    for char in text:
        letter = letters[char].translated(offsetX, offsetY)
       
        lines = repr(letter).split('\n')  # Split the representation by lines
        flag = 0
        for line in lines:
                
            if line.strip():  # Check if the line is not empty
                if not line.startswith(('m', 'M')):  # Check if the line starts with 'm' or 'M'
                    line += ' F1500'  # Add ' F1500' to the line
                gcodeLettersArray.append(line)
            if flag==0:
                gcodeLettersArray.append('m5')
                flag=1

        if not skipNextLine:  # Increment offsets unless we're skipping the next line
            offsetX += letter.width + padding
            if offsetX >= lineLength:
                offsetX = 0
                offsetY -= lineSpacing
        gcodeLettersArray.append('m3')

    # Call the rescale_gcode function to rescale the generated G-code
    scaled_gcode = rescale_gcode(gcodeLettersArray)

    return "\n".join(scaled_gcode)


@app.route('/convert', methods=['POST'])
def convert_text_to_gcode():
    data = request.json['text']
    namespace = argparse.Namespace()
    namespace.line_length = 300
    namespace.line_spacing = 10
    namespace.padding = 3
    letters = readLetters("C:\\Users\\sabit\\OneDrive\\Desktop\\V3")
    gcode = textToGcode(letters, data, namespace.line_length, namespace.line_spacing, namespace.padding)

    return jsonify({'gcode': gcode.split('\n')})  # Split the gcode string into a list of lines

if __name__ == '__main__':
    app.run(debug=True)
