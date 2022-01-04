import binascii
import csv
import random
from base64 import b64encode

'''
A Set of helper functions.

'''


def binary_to_string(n):
    # Helper function that will return ascii from binary
    # Use this to get the original message from a binary number
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()


def string_to_binary(string):
    # Helper function that will return binary from string
    # Use this to get a number from the message
    return int.from_bytes(string.encode(), 'big')


def binary_to_binary_string(binary):
    # Helper function that will return binary as a bit string from binary
    # Use this to convert the binary number into a string of 0s and 1s.
    # This is needed to generate the appropriate random key
    return bin(binary)[2:]


def binary_string_to_binary(bin_string):
    # Helper function that will return binary from a bit string
    # Use this to convert the random key into a number for calculations
    return int(bin_string, 2)


def get_random_bit():
    # Helper function that will randomly return either 1 or 0 as a string
    # Use this to help generate the random key for the OTP
    return str(random.randint(0, 1))


def read_message():
    # Helper function that will read and process message.txt which will provide a good tessting message
    message = ''
    f = open('message.txt', 'r')
    for line in f:
        message += line.replace('\n', ' ').lower()
    return message


class Cipher:

    def __init__(self):
        """
        Initialize the suite
        In part 1 create letter_dict and inverse_dict
        In part 3 create letter_heuristics and call self.read_csv()
        self.letter_dict: use a dictionary tp map letters to numbers. For example, call self.letter_dict['b'] then get 1
        self.inverse_dict: creat another dictionary which swap key-value pair from self.letter_dict to map numbers to letters. For example, call self.inverse_dict[1] then get 'b'.
        self.letter_heuristics: Show the occurrence of each letter in sentence when reading csv file. For example, self.letter_heuristics['e'] to get the frequency of e showed up in the csv file.
        self.wordlist: reading words from wordlist file for extra credits part breaking vignere
        self.read_csv: read csv file
        """
        self.letter_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7,
                            'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14,
                            'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20,
                            'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z': 25, ' ': 26}
        self.inverse_dict = {v: k for k, v in self.letter_dict.items()}
        self.letter_heuristics = {}
        self.wordlist = []
        self.read_csv()

    
    def rotate_letter(self, letter, n):
        """
        Rotate a letter by n and return the new letter
        if n = 1, letter = z, it return space
        if n = 2, letter = a, it return c
        if n = 2, letter = z, it return a
        """
        num = self.letter_dict[letter] 
        return self.inverse_dict[(num + n) % 27]  

    def encode_caesar(self, message, n):
        """
        Encode message using rotate_letter on every letter and return the cipher text
        input message return string res which every character pushed back n positions
        """
        res = ""

        for ch in message:
            # every character pushed back n positions is equal to find the character which after n than original character
            r = self.rotate_letter(ch, n)
            res += r
        return res

    def decode_caesar(self, cipher_text, n):
        """
        Decode a cipher text by using rotate_letter the opposite direction and return the original message
        """
        res = ""
        for ch in cipher_text:
            # rotate backward number = -n= n*-1
            r = self.rotate_letter(ch, n * -1)
            res += r
        return res

    def read_csv(self):
        """
        Read the letter frequency csv and create a heuristic save in a class variable
        we need to calculate total frequency to score decoded sentences
        """
        file = 'letter_frequencies.csv'
        f = open(file, "r+")
        tot = 0
        for line in f:
            # to replace \n and lowercase all for organizing data
            r = line.lower().replace("\n", "")
            # unpack data of every line
            k, v = r.split(",")
            # we need a if statement here since the first line is headline
            if v != 'count (in billions)':
                # record every frequency corresponded with each letter
                self.letter_heuristics[k] = float(v)
                tot += float(v)
        # change frequency into frequency percentage
        # for i in self.letter_heuristics:
        #     self.letter_heuristics[i] = self.letter_heuristics[i] / tot
        f.close()
        # print(self.letter_heuristics)

    def score_string(self, string):
        """
        Score every letter of a string based on the self.letter_heuristics[i] / total
        calculate the frequency of each letter in the string then compare it with the frequency of each letter in self.letter_heuristics
        assume every letter full score is 100, the current score will be 100-(frequency percentage difference)*100
        the bigger frequency percentage difference the lower score is
        finally add every score then return the total score of whole string
        """
        # Score every letter of a string and return the total
        # dist = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0,
        #         'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0,
        #         'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0,
        #         'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0, ' ': 0}
        score = 0.0
        for ch in string:
            score += self.letter_heuristics[ch]

        return score
        # for ch in string:
        #     dist[ch] += 1
        # tot = len(string)
        # for i in dist:
        #     dist[i] = dist[i] / tot
        # score = 0
        # for i in dist:
        #     r = 100 - abs(self.letter_heuristics[i] - dist[i]) * 100
        #     score += r
        # return score

    def crack_caesar(self, cipher_text):
        """
        Break a caesar cipher by finding and returning the most probable outcome
        there are 27 cases from moving 0 position to 26 positions, which means the same result between moving 0 and moving 27.
        By enumerate 26 letters and moving backwards, we can calculate decoded sentence.
        Then we score decoded sentence using score_string(self, string), we will keep one sentence which has the highest score as final decoding result.
        """
        # create a list to store sentence among 27 cases
        deStr = []
        # create a list to store the every score corresponded with each sentence in list named de_Str
        scores = []
        # 27 cases from moving 0 position to 26 position
        for i in range(27):
            # decoded sentence at the current moving position
            s = ""
            for ch in cipher_text:
                r = self.rotate_letter(ch, i * -1)
                s += r
            # add the decoded sentence into list
            deStr.append(s)
            # add the score of the current decoded sentence into list
            scores.append(self.score_string(s))
        # finding the highest score and corresponded index
        Max = 0
        Maxi = -1
        for i in range(27):
            if scores[i] > Max:
                Max = scores[i]
                Maxi = i
        # print("================================")
        # print(deStr[Maxi])
        return deStr[Maxi]


    def encode_vigenere(self, message, key):
        """
        Encode message using rotation by key string characters
        caesar use the same rotation parameter
        but vigenere use the changing rotation parameter
        key is the password string for rotation
        """
        l = len(message)
        kl = len(key)
        res = ""
        for i in range(l):
            # once we run out of key, we need to start back at the beginning of it
            num = self.letter_dict[key[i % kl]]
            r = self.rotate_letter(message[i], num)
            res += r

        return res

    def decode_vigenere(self, cipher_text, key):
        """
        Decode ciphertext using rotation by key string characters
        exactly same process except being backwards
        """
        l = len(cipher_text)
        kl = len(key)
        res = ""
        for i in range(l):
            num = self.letter_dict[key[i % kl]]
            r = self.rotate_letter(cipher_text[i], num * (-1))
            res += r

        return res

    def encode_otp(self, message):
        """
        suppose message is 5 bits，key(password string) is 3 bits
        5^3 ==> (101)^(011)
                    101
                  ^ 011
                    ———
                    110
        cipher_text is 110, decoded message is 6
        if two corresponded numbers are different，then result is 1; if two corresponded numbers are the same，then result is 0
        decoding process is the same as encoding process
        cipher_text^3(key) ==>  (110)^(011)
                    110
                  ^ 011
                    ———
                    101
        cipher_text is 101, decoded message is 5
        after two times XOR, number x is x      x^y^y=x
        OTP, the first time XOR is encode, and the second XOR is decode
        """
        # Similar to a vernan cipher, but we will generate a random key string and return it
        numeric_message = string_to_binary(message)
        # we need to turn integer into the binary string. For example, turn 5 to 101. We want to know how many digits of this binary string same as the length of decoded string
        bin_message = binary_to_binary_string(numeric_message)
        # to store random binary string with same length
        bin_str = ""
        # generate random binary string with the same length as bin_message as the key(password string) of OTP
        for i in bin_message:
            n = get_random_bit()
            bin_str += n
        # now we have a random binary string with the same length as the message which need to be encoded
        # we have to change this random binary string to numbers since only numbers can do XOR
        bin_key = binary_string_to_binary(bin_str)
        # using XOR to process the numbers then we will get cipher_text
        code = numeric_message ^ bin_key

        return code, bin_key

    def decode_otp(self, cipher_text, key):
        """ XOR cipher text and key. Convert result to string"""
        # OTP, the first time XOR is encode, and the second XOR is decode
        res = cipher_text ^ key
        # the original message is string
        deCode = binary_to_string(res)
        return deCode
        # return None

    def read_wordlist(self):
        """
        Extra Credit: Read all words in wordlist and store in list. Remember to strip the endline characters
        read wordlist then use it for crack vigenere
        """
        filename = "wordlist.txt"
        f = open(filename, "r+")
        for line in f:
            self.wordlist.append(line.strip())


    def crack_vigenere(self, cipher_text):
        """
        Extra Credit: Break a vigenere cipher by trying common words as passwords
        Return both the original message and the password used
        we need to read all words from wordlist file, then calculate the score of decoded sentence one by one
        So, we consider the sentence with the highest score as the final result
        """

        # take 10000 words in wordlist file as the key(password string)
        self.read_wordlist()
        # print(cipher_text)
        # the sentence with highest score
        best_decode = ""
        # the key of the sentence with highest score
        best_key = ""
        # highest score
        Max = 0
        for word in self.wordlist:
            # using current word to decode and save decoded sentence
            res = self.decode_vigenere(cipher_text, word)
            # score every sentence
            score = self.score_string(res)
            # update the highest score and corresponded word and sentence
            if Max < score:
                Max = score
                best_decode = res
                best_key = word

        return best_decode, best_key


print("---------------------TEST CASES---------------------------")
cipher_suite = Cipher()
print("---------------------PART 1: CAESAR-----------------------")
message = read_message()
cipher_text = cipher_suite.encode_caesar(message, 5)
print('Encrypted Cipher Text:', cipher_text)
decoded_message = cipher_suite.decode_caesar(cipher_text, 5)
print('Decoded Message:', decoded_message)
print("------------------PART 2: BREAKING CAESAR------------------")
cracked = cipher_suite.crack_caesar(cipher_text)
print('Cracked Code:', cracked)
print("---------------------PART 3: Vignere----------------------")
password = 'dog'
print('Encryption key: ', password)
cipher_text = cipher_suite.encode_vigenere(message, password)
print('Encoded:', cipher_text)
decoded_message = cipher_suite.decode_vigenere(cipher_text, password)
print('Decoded:', decoded_message)

print("-----------------------PART 4: OTP------------------------")

cipher_text, key = cipher_suite.encode_otp(message)
decoded = cipher_suite.decode_otp(cipher_text, key)
print('Cipher Text:', cipher_text)
print('Generated Key:', key)
print('Decoded:', decoded)

print('---------PART 5: Breaking Vignere (Extra Credit)----------')
cracked, pwrd = cipher_suite.crack_vigenere(message)
print('Cracked Code:', cracked)
print('Password:', pwrd)
