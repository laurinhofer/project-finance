def is_valid_email(email):
    return (
        len(email) <= 256 and
        "@" in email and
        "." in email and
        email.index("@") > 0 and
        not email.endswith("@")
    )


def calculate_price(schrauben, muttern, unterlegscheiben):
    gesamt_cent = schrauben * 7 + muttern * 4 + unterlegscheiben * 2
    return gesamt_cent / 100

schrauben = int(input())
muttern = int(input())
unterlegscheiben = int(input())

preis = calculate_price(schrauben, muttern, unterlegscheiben)
print(f"Der Endpreis beträgt: {preis:.2f} Euro")


def get_area(a, c, h):
    return ((a + c) * h) / 2

seite_a = float(input())
seite_c = float(input())
hoehe = float(input())

flaeche = get_area(seite_a, seite_c, hoehe)
print(f"Der Flächeninhalt beträgt: {flaeche}")



def groessere_zahl(a, b):
    return a > b

a = int(input())
b = int(input())

print(groessere_zahl(a, b))



def mult(a, b):
    if a <= b:
        for i in range(a, b + 1):
            print(f"{i} mal {b} ist gleich {i * b}")
    else:
        for i in range(b, a + 1):
            print(f"{a} mal {i} ist gleich {a * i}")
 
z1 = int(input())
z2 = int(input())
 
mult(z1, z2)



dna = list(input())
count = [["A", 0], ["C", 0], ["T", 0], ["G", 0]]

for base in dna:
    for entry in count:
        if base == entry[0]:
            entry[1] += 1

print(f"A: {count[0][1]}, C: {count[1][1]}, T: {count[2][1]}, G: {count[3][1]}")



food = ["Burger", "Falafel", "Döner", "Kebab", "Schnitzelsemmel"]
word = input()

if word in food:
    food.remove(word)
    print(food)
else:
    print("Wort nicht gefunden")



words = []
while True:
    word = input()
    if word == "Stop":
        break
    words.append(word)

for w in words:
    print(f"Das Wort {w} hat {len(w)} Buchstaben.")




a_list = ["HTL", "Anich", "Elektronik", "FSST", "HTL", "Python", "Anich"]
found = []

while True:
    word = input()
    if word == "Stop":
        break
    if word in a_list:
        found.append(word)

print(found)



nums1=[1,3,9,2,1,9]
nums2=[4,2,9,1]

combined = nums1 + nums2 

for n in combined:
    print(n)



numbers = [int(input()) for _ in range(5)]
print(numbers)
remove = int(input())
print([x for x in numbers if x != remove])



numbers = [int(input()) for _ in range(5)]
squares = [x**2 for x in numbers]
print(numbers)
print(squares)
