import fastavro

# Specify the path to the Avro file
file_path = "jobs.avro"

# Open the Avro file in read mode
with open(file_path, "rb") as avro_file:
    # Read the Avro file using fastavro
    avro_reader = fastavro.reader(avro_file)

    # Iterate over each record in the Avro file
    for record in avro_reader:
        # Process each record as needed
        print(record)