import bcrypt
hash_str = b"$2b$12$tiZPcMjelNHafsONOcZZ/e9U3o39uymiOVmr4YBhkSi4pZtmp.fk2"
print(bcrypt.checkpw(b"adminpassword", hash_str))
