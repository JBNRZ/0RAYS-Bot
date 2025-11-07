from hashlib import sha1
from base64 import b64decode, b64encode
from xml.etree import ElementTree
from Crypto.Cipher import AES
from socket import ntohl, htonl
from struct import unpack, pack
from random import sample
from string import ascii_letters, digits
from time import time

AES_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>"""


def get_random_string() -> str:
    return "".join(sample(ascii_letters + digits, 16))


def sign(token: str, timestamp: str, nonce: str, encrypted: str) -> str:
    return sha1("".join(sorted([token, timestamp, nonce, encrypted])).encode()).hexdigest()


def extract(xml: str):
    tree = ElementTree.fromstring(xml)
    encrypted = tree.find("Encrypt").text
    name = tree.find("ToUserName").text
    return encrypted, name


def generate(encrypted: str, signature: str, timestamp: str, nonce: str) -> str:
    resp_dict = {
        'msg_encrypt': encrypted,
        'msg_signaturet': signature,
        'timestamp': timestamp,
        'nonce': nonce,
    }
    return AES_TEXT_RESPONSE_TEMPLATE % resp_dict


def content(xml: str) -> str:
    tree = ElementTree.fromstring(xml)
    if tree.find("MsgType").text == "image":
        return tree.find("PicUrl").text
    elif tree.find("MsgType").text == "event":
        return tree.find("Event").text
    else:
        return tree.find("Content").text


class PKCS7Encoder:

    block_size = 32

    def encode(self, text: bytes) -> bytes:
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        return text + chr(amount_to_pad).encode() * amount_to_pad


class PrpCrypt:

    def __init__(self, key: bytes):
        self.key = key
        self.mode = AES.MODE_CBC

    def decrypt(self, msg: str, appid: str) -> str:
        aes = AES.new(self.key, self.mode, self.key[:16])
        msg = aes.decrypt(b64decode(msg.encode()))
        msg = msg[16:-msg[-1]]
        xml_len = ntohl(unpack("I", msg[: 4])[0])
        xml_content = msg[4: xml_len + 4].decode()
        from_appid = msg[xml_len + 4:].decode()
        assert from_appid == appid
        return xml_content

    def encrypt(self, text: str, appid: str) -> str:
        text = get_random_string().encode() + pack("<I", htonl(len(text))) + text.encode() + appid.encode()
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        return b64encode(cryptor.encrypt(text)).decode()


class WXCrypt:

    def __init__(self, sToken: str, sEncodingAESKey: str, sAppId: str):
        self.key = b64decode(sEncodingAESKey + "=")
        assert len(self.key) == 32
        self.token = sToken
        self.appid = sAppId

    def decrypt(self, sPostData: str, sMsgSignature: str, sTimestamp: str, sNonce: str) -> str:
        msg, name = extract(sPostData)
        signed = sign(self.token, sTimestamp, sNonce, msg)
        assert signed == sMsgSignature
        return PrpCrypt(self.key).decrypt(msg, self.appid)

    def encrypt(self, sReplay: str, sNonce: str, timestamp: str = None) -> str:
        pc = PrpCrypt(self.key)
        encrypt = pc.encrypt(sReplay, self.appid)
        timestamp = str(round(time())) if timestamp is None else timestamp
        signature = sign(self.token, timestamp, sNonce, encrypt)
        return generate(encrypt, signature, timestamp, sNonce)
