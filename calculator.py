
MULTIPLY = '*'
DIVIDE = '/'
ADD = '+'
SUBTRACT = '-'
EXPONENT = '^'
variables = {}

operators = {MULTIPLY, DIVIDE, ADD, SUBTRACT, EXPONENT}


def input_reader(user_string: str):
    if user_string == "quit" or user_string == "q!":
        return False
    else:
        return user_string.split(',')


def interpret_expression_types(expressions: list):
    expr_dict = {}
    expr_list = []

    for i in range(0, len(expressions)):
        trimmed_expression, expression_type, variables_found, var_to_assign = find_variables_if_any(
            expressions[i])

        name = f"Expression #{i+1}"
        if "Invalid" in expression_type:
            expr_dict[name] = {
                'error_type': expression_type,
                'type': 'Invalid Expression'
            }
            expr_list.append(expr_dict[name]['error_type'])
            continue
        else:
            expr_dict[name] = {
                'list': convert_to_postfix(trimmed_expression),
            }
            if isinstance(expr_dict[name]['list'], str):
                expr_dict[name]['type'] = 'Invalid Expression'
                expr_list.append(expr_dict[name]['list'])
            else:
                expr_dict[name]['type'] = expression_type
                print
                expr_list.append(calculate_expression(
                    expr_dict[name]['list'], var_to_assign))

    return expr_list


def find_variables_if_any(user_string: str):
    variable_found = False
    equals_found = False
    var_to_assign = ''
    variables_found = []
    last_char = ''
    for i in range(0, len(user_string)):
        if len(user_string) == 1:
            return user_string, "Single Operand Only", None, None
        elif user_string[i].isalpha() and i == 0 or user_string[i].isalpha() and i == len(user_string) - 1:
            if not variable_found and last_char == '=' and not equals_found or not variable_found and user_string[1] == '=' and not equals_found:
                variable_found = True
                equals_found = True
                variables_found.append(user_string[i])
                variables[user_string[i]] = None
        elif user_string[i].isalpha() and not last_char or user_string[i].isalpha() and last_char == '(' or user_string[i].isalpha() and last_char in operators:
            variable_found = True
            variables_found.append(user_string[i])
        elif user_string[i] == '=' and i != 1 and user_string[i] == '=' and i != len(user_string) - 2:
            if i == 0 or i == len(user_string) - 1:
                return None, "Invalid Expression: No variable declared to assign value.", None, None
            else:
                return None, "Invalid Expression: '=' in the middle of expression.", None, None
        elif user_string[i] in operators or user_string[i] == '(' or user_string[i] == ')' or user_string[i].isdigit() or user_string[i] == '.':
            pass
        else:
            pass

        last_char = user_string[i]
    if variable_found and equals_found and len(variables_found) > 1:
        if user_string[1] == '=':
            trimmed_string = user_string[2:]
            var_to_assign = variables_found[0]
            return trimmed_string, "var_equals_expression_and_variables", variables_found, var_to_assign
        else:
            trimmed_string = user_string[:-2]
            var_to_assign = variables_found[len(variables_found) - 1]
            return trimmed_string, "var_equals_expression_and_variables", variables_found, var_to_assign
    elif variable_found and equals_found and len(variables_found) == 1:
        if user_string[1] == '=':
            trimmed_string = user_string[2:]
            var_to_assign = variables_found[0]
            return trimmed_string, "var_equals_expression_only", variables_found, var_to_assign
        else:
            trimmed_string = user_string[:-2]
            var_to_assign = variables_found[len(variables_found) - 1]
            return trimmed_string, "var_equals_expression_only", variables_found, var_to_assign
    elif variables_found and not equals_found:
        return user_string, "var_in_expression_only", variables_found, None
    else:
        return user_string, "normal_expression", variables_found, None


def calculate_expression(expression: list, var):
    stack = []
    for item in expression:
        if item == EXPONENT:
            result = float(stack.pop(-2)) ** float(stack.pop(-1))
            stack.append(float(result))
        elif item == MULTIPLY:
            result = float(stack.pop(-2)) * float(stack.pop(-1))
            stack.append(float(result))
        elif item == DIVIDE:
            if float(stack[-1]) == 0:
                return "Undefined: Division By Zero in Expression"
            result = float(stack.pop(-2)) / float(stack.pop(-1))
            stack.append(float(result))
        elif item == ADD:
            result = float(stack.pop(-2)) + float(stack.pop(-1))
            stack.append(float(result))
        elif item == SUBTRACT:
            result = float(stack.pop(-2)) - float(stack.pop(-1))
            stack.append(result)
        elif item.isalpha() and item not in variables:
            return f"Invalid Expression: Unassigned Variable {item}"
        elif item.isalpha() and item in variables:
            stack.append(variables[item])
        else:
            stack.append(item)
    result = stack[0]

    if result > 10000000 or result < 0.00000001:
        result = "{:e}".format(result)
        variables[var] = result
        return result
    elif result.is_integer():
        variables[var] = int(result)
        return int(result)
    else:
        variables[var] = result
        return result


def get_operator_priority(operator):
    if operator == ADD or operator == SUBTRACT:
        return 3
    elif operator == MULTIPLY or operator == DIVIDE:
        return 2
    elif operator == EXPONENT:
        return 1
    else:
        return 4


def convert_to_postfix(equation: str):

    operator_stack = []
    postfix_expression = []
    current_integer = ""
    last_char = ""
    has_decimal = False
    has_operator = False

    for char in equation:
        if char == '.' and not has_decimal:
            current_integer += char
            has_decimal = True
        elif char == '.' and has_decimal:
            return "Invalid Expression: Multiple decimal points in numbers."
        elif char == SUBTRACT and last_char in operators or char == SUBTRACT and not last_char:
            current_integer += char
        elif operator_stack and char in operators:
            has_operator = True
            if current_integer:
                postfix_expression.append(current_integer)
                has_decimal = False
            priority = get_operator_priority(char)

            while operator_stack and get_operator_priority(operator_stack[-1]) <= priority:
                postfix_expression.append(operator_stack.pop())

            operator_stack.append(char)
            current_integer = ""
        elif char in operators:
            has_operator = True
            if current_integer:
                postfix_expression.append(current_integer)
                has_decimal = False
            current_integer = ""
            operator_stack.append(char)
        elif char.isdigit():
            current_integer += char
        elif char == '(':
            if current_integer:
                postfix_expression.append(current_integer)
                has_decimal = False
            operator_stack.append(char)
            current_integer = ""
        elif char == ')' and '(' not in operator_stack:
            return "Invalid Expression: Unbalanced Parentheses"
        elif char == ')':
            if current_integer:
                postfix_expression.append(current_integer)
            while operator_stack and operator_stack[-1] != '(':
                postfix_expression.append(operator_stack.pop())
            operator_stack.pop()
            current_integer = ""
        elif char.isalpha():
            postfix_expression.append(char)
        else:
            return "Invalid Expression: Unsupported Characters"

        last_char = char

    if current_integer:
        postfix_expression.append(current_integer)

    while operator_stack:
        postfix_expression.append(operator_stack.pop())

    if '(' in postfix_expression:
        return "Invalid Expression: Unbalanced Parentheses"
    elif has_operator == False:
        return postfix_expression[0]
    else:
        return postfix_expression


def main():
    is_using = True
    while is_using:
        user_input = input_reader(input(
            "Type a mathematical expression or input multiple expressions by separating with a comma: ").replace(" ", "").lower())
        if user_input == False:
            is_using = False
            continue
        print(interpret_expression_types(user_input))


main()
