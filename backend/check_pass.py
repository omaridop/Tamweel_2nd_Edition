import bcrypt

hash_str = b'$2b$12$httd3EaqHnvWF4s2g1ZJVuVqYygPiOVk0bSCXaArR8G4COUGov8Fy'
print('Matches adminpassword?', bcrypt.checkpw(b'adminpassword', hash_str))
print('Matches password123?', bcrypt.checkpw(b'password123', hash_str))
