# Write your solution here
points = int(input('How many points [0-100]'))

grades = [
    (-float("inf"), 0, "impossible!"),
    (0, 50, "fail"),
    (50, 60, '1'),
    (60, 70, '2'),
    (70, 80, '3'),
    (80, 90, '4'),
    (90, 101, '5'),
    (101, float("inf"), "impossible!")
]


def grade(points):
    for low, high, label in grades:
        if points >= low and points < high:
            return label


print(f'Grade: {grade(points)}')