import getopt
import sys

def main():
    try:
        # Analizar los argumentos de la línea de comandos
        opts, args = getopt.getopt(sys.argv[1:], "i:o:")
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    input_file = None
    output_file = None

    # Asignar valores a las variables dependiendo de los argumentos pasados
    for opt, arg in opts:
        if opt == "-i":
            input_file = arg
        elif opt == "-o":
            output_file = arg

    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()

