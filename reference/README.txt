This unchanged automated contract was reviewed before the original implementation.
Original test commit: 563359bb8ba36d246f078c80ed8bf2282c62a2bd
It records all previously agreed negative/zero/power decisions before any redo implementation.
It is preserved as a reference outside tests/ and is not counted as a new failing test in redo cycle 1.
The new sequential tests are recorded separately; original history is not rewritten.
