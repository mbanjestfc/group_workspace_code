# Import the modules
import os
import datetime
import subprocess

# Define a function to calculate the age in months and years from a date
def age(date):
  # Get the current date and the input date
  current_date = datetime.datetime.now()
  input_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f %z")
  # Calculate the difference in days
  diff = (current_date - input_date).days
  # Convert the difference to months and years
  months = diff // 30
  years = months // 12
  # Return the result
  return f"{months} months, {years} years"

# Loop through all the group work spaces
for gws in os.listdir("/gws"):
  # Get the full path of the group work space
  path = os.path.join("/gws", gws)
  # Get the creation date, disk usage, disk quota and last access date
  creation_date = subprocess.getoutput(f"stat -c %w {path}")
  disk_usage = subprocess.getoutput(f"du -sh {path} | cut -f1")
  disk_quota = subprocess.getoutput(f"quota -s {path} | tail -n1 | awk '{{print $3}}'")
  last_access_date = subprocess.getoutput(f"stat -c %x {path}")
  # Calculate the age in months and years from the creation date
  age = age(creation_date)
  # Count the number of unique users in the group work space
  users = len(set(subprocess.getoutput(f"find {path} -type f -printf '%u\n'").split()))
  # Write the output to a text file
  with open("output.txt", "a") as f:
    f.write(f"{path}, {age}, {creation_date}, {disk_usage}, {disk_quota}, {last_access_date}, {users}\n")
