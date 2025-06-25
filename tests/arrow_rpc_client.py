import pyarrow as pa
import pyarrow.flight

# only used for testing
client = pa.flight.connect("grpc://127.0.0.1:8101")
# Upload a new dataset
data_table = pa.table(
    [['hammer', 'wrench', 'screwdriver', 'towel'], [8, 3, 6, 11], [5, 7, 4, 3], [14,0,0,0]],
    names=["A", "b", "w", "W_max"]
)

upload_descriptor = pa.flight.FlightDescriptor.for_path("python_glpk_param")
writer, _ = client.do_put(upload_descriptor, data_table.schema)
writer.write_table(data_table)
writer.close()


# Retrieve metadata of newly uploaded dataset
flight = client.get_flight_info(upload_descriptor)
descriptor = flight.descriptor

# Read content of the dataset
reader = client.do_get(flight.endpoints[0].ticket)
read_table = reader.read_all()

# Drop the newly uploaded dataset

result_reader = client.do_get(pa.flight.Ticket(b"do_solver,python_glpk_param,pyomo.glpk_solver_example"))
client.do_action(pa.flight.Action("drop_dataset", "python_glpk_param".encode('utf-8')))

print(result_reader.read_all().to_pandas())
# List existing datasets.
for flight in client.list_flights():
    descriptor = flight.descriptor
    print("Path:", descriptor.path[0].decode('utf-8'), "Rows:", flight.total_records, "Size:", flight.total_bytes)
    print("=== Schema ===")
    print(flight.schema)
    print("==============")
    print("")