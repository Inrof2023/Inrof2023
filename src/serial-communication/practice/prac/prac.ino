void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int line_array[4] = {1, 2, 3, 4}
  for (i = 0; i < 4 - 1; i++) {
    Serial.print(line_array[i]);
    Serial.print(",");
  }
  Serial.println(line_array[i]);

  while (Serial.available() <= 0) {
  }
  Serial.readBytes(data, BUFFER_SIZE);
  Serial.print(data[0]);
  Serial.print(data[1]);
  Serial.print(data[2]);
  Serial.print(data[3]);
}