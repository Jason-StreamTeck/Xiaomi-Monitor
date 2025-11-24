### Identified both of the below characteristics display the temperature and humidity
8edfffef-3d1b-9c37-4623-ad7265f14076 ['read', 'notify']
ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6 ['notify', 'read']

### Conclusion
Use 'ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6' as the other characteristic could not access notify. (To be put into the `MI_CHARACTERISTIC` field of the `.env` file)

### List of Services and Characteristics provided by `Mi Temperature and Humidity Monitor 2`

- [Service] 00001800-0000-1000-8000-00805f9b34fb | Generic Access Profile
  - [Characteristic] 00002a00-0000-1000-8000-00805f9b34fb | Device Name | ['notify', 'read']
  - [Characteristic] 00002a01-0000-1000-8000-00805f9b34fb | Appearance | ['read']
  - [Characteristic] 00002a04-0000-1000-8000-00805f9b34fb | Peripheral Preferred Connection Parameters | ['read']
- [Service] 00001801-0000-1000-8000-00805f9b34fb | Generic Attribute Profile
  - [Characteristic] 00002a05-0000-1000-8000-00805f9b34fb | Service Changed | ['indicate']
- [Service] 0000180a-0000-1000-8000-00805f9b34fb | Device Information
  - [Characteristic] 00002a24-0000-1000-8000-00805f9b34fb | Model Number String | ['read']
  - [Characteristic] 00002a25-0000-1000-8000-00805f9b34fb | Serial Number String | ['read']
  - [Characteristic] 00002a26-0000-1000-8000-00805f9b34fb | Firmware Revision String | ['read']
  - [Characteristic] 00002a27-0000-1000-8000-00805f9b34fb | Hardware Revision String | ['read']
  - [Characteristic] 00002a28-0000-1000-8000-00805f9b34fb | Software Revision String | ['read']
  - [Characteristic] 00002a29-0000-1000-8000-00805f9b34fb | Manufacturer Name String | ['read']
- [Service] 00010203-0405-0607-0809-0a0b0c0d1912 | Unknown
  - [Characteristic] 00010203-0405-0607-0809-0a0b0c0d2b12 | Unknown | ['notify', 'write-without-response', 'read']
- [Service] ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown
  - [Characteristic] ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'read']
  - [Characteristic] ebe0ccb9-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['read']
  - [Characteristic] ebe0ccba-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'read']
  - [Characteristic] ebe0ccbb-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['read']
  - [Characteristic] ebe0ccbc-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['notify']
  - [Characteristic] ebe0ccbe-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'read']
  - [Characteristic] ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['notify', 'read']
  - [Characteristic] ebe0ccc4-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['read']
  - [Characteristic] ebe0ccc8-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write']
  - [Characteristic] ebe0ccd1-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write']
  - [Characteristic] ebe0ccd7-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'read']
  - [Characteristic] ebe0ccd8-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write']
  - [Characteristic] ebe0ccd9-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'notify']
  - [Characteristic] ebe0cff1-7a0a-4b0c-8a1a-6ff2997da3a6 | Unknown | ['write', 'read']
- [Service] fafafa00-fafa-fafa-fafa-fafafafafafa | Unknown
  - [Characteristic] fafafa01-fafa-fafa-fafa-fafafafafafa | Unknown | ['write', 'read']
- [Service] 8edffff0-3d1b-9c37-4623-ad7265f14076 | Unknown
  - [Characteristic] 8edffff1-3d1b-9c37-4623-ad7265f14076 | Unknown | ['read']
  - [Characteristic] 8edffff3-3d1b-9c37-4623-ad7265f14076 | Unknown | ['notify']
  - [Characteristic] 8edffff4-3d1b-9c37-4623-ad7265f14076 | Unknown | ['write', 'read']
  - [Characteristic] 8edfffef-3d1b-9c37-4623-ad7265f14076 | Unknown | ['notify', 'read']
- [Service] 0000fe95-0000-1000-8000-00805f9b34fb | Xiaomi Inc.
  - [Characteristic] 00000004-0000-1000-8000-00805f9b34fb | Vendor specific | ['read']
  - [Characteristic] 00000010-0000-1000-8000-00805f9b34fb | UPNP | ['notify', 'write-without-response']
  - [Characteristic] 00000017-0000-1000-8000-00805f9b34fb | AVCTP | ['write', 'notify']
  - [Characteristic] 00000018-0000-1000-8000-00805f9b34fb | Vendor specific | ['notify', 'write-without-response']
  - [Characteristic] 00000019-0000-1000-8000-00805f9b34fb | AVDTP | ['notify', 'write-without-response']
  - [Characteristic] 0000001a-0000-1000-8000-00805f9b34fb | Vendor specific | ['notify', 'write-without-response']
  - [Characteristic] 0000001b-0000-1000-8000-00805f9b34fb | CMTP | ['notify', 'write-without-response']
  - [Characteristic] 0000001c-0000-1000-8000-00805f9b34fb | Vendor specific | ['notify', 'write-without-response']