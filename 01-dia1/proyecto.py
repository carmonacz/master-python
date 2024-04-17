# Debes construir un progrma que haga lo siguiente:
# 1- Frase de saludo inicial.
# 2- Entrada del usuario preguntando el nombre.
# 3- Entrada del usuario preguntando la edad.
# 4- Entrada del usuario preguntando el país de nacimiento.
# 5- Comentarios en cada sección del código.
# 6- Vas a tener que presentar los datos recogidos del usuario e imprimirlos en una frase final.
# Debes utilizar saltos de línea en todo el código, donde consideres necesario para que todo quede lo mejor presentado posible en la consola

#Saludo de bienvenida
frase_saludo = "Hola, le voy a relizar unas preguntas para conocerle mejor.\n"
print(frase_saludo)

#Entradas del usuario preguntando nombre, edad y país de nacimiento
nombre = input("Introduzca su nombre:\n")
print("")
edad = input("Introduzca su edad:\n")
print("")
pais = input("Introduzca su país de nacimiento:\n")
print("")
print(f"Hola, {nombre}. Usted tiene {edad} años y nació en {pais}.")