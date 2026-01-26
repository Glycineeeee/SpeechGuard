================================================================================
                     SpeechGuard - Sample Audio Files
================================================================================

This directory contains demonstration examples of SpeechGuard's privacy
protection capabilities, showcasing both acoustic and content privacy features.

================================================================================
FILE NAMING CONVENTION
================================================================================

Three audio samples are provided in both WAV (lossless) and MP3 (lossy) formats:

  *_ori.wav/mp3  - Original unprotected audio
  *_pro.wav/mp3  - Protected audio (acoustic + content privacy applied)
  *_rec.wav/mp3  - Recovered audio (using correct decryption keys)

================================================================================
AUDIO TRANSCRIPTIONS
================================================================================

Sample 1:
  "ALSO A POPULAR CONTRIVANCE WHEREBY LOVE MAKING MAY BE SUSPENDED BUT NOT
   STOPPED DURING THE PICNIC SEASON"

Sample 2:
  "SOME HAVE ACCEPTED IT AS A MIRACLE WITHOUT PHYSICAL EXPLANATION"

Sample 3:
  "ASK HER TO BRING THESE THINGS WITH HER FROM THE STORE"

================================================================================
CONTENT PRIVACY PROTECTION
================================================================================

The following sensitive phrases have been encrypted in the protected versions:

  Sample 1: "LOVE MAKING"        (encrypted segment)
  Sample 2: "MIRACLE"            (encrypted segment)
  Sample 3: "FROM THE STORE"     (encrypted segment)

When listening to the "_pro" files, you will notice:
  - Encrypted segments sound distorted/unintelligible
  - Non-sensitive parts remain clear and understandable
  - Overall speech flow is maintained

In the "_rec" files (recovered with correct keys):
  - All segments are restored to original quality
  - Demonstrates reversibility for authorized users

================================================================================
ACOUSTIC PRIVACY PROTECTION
================================================================================

In addition to content encryption, all protected files have undergone
frequency warping transformation to protect speaker identity:

  - Voice characteristics are altered
  - Speech remains intelligible
  - Speaker identity is protected
  - Reversible with correct parameters (as shown in "_rec" files)

================================================================================
LISTENING GUIDE
================================================================================

1. Listen to original files (*_ori.*):
   - Clear, unprotected speech
   - Original speaker voice characteristics

2. Listen to protected files (*_pro.*):
   - Altered voice characteristics (acoustic privacy)
   - Encrypted segments are unintelligible (content privacy)
   - Non-sensitive content remains understandable

3. Listen to recovered files (*_rec.*):
   - Restored to original quality
   - Demonstrates authorized recovery capability

================================================================================
TECHNICAL NOTES
================================================================================

- WAV files: Lossless quality, larger file size
- MP3 files: Lossy compression, smaller file size, suitable for distribution
- Encryption: AES-128, unique key per segment
- Frequency warping: Multi-segment linear VTLN
- Sample rate: 16 kHz
- Format: Mono channel

================================================================================
USE CASES DEMONSTRATED
================================================================================

These samples demonstrate SpeechGuard's ability to:

  ✓ Protect sensitive information in conversations
  ✓ Maintain overall speech intelligibility
  ✓ Protect speaker identity
  ✓ Enable authorized recovery
  ✓ Work with common audio formats (WAV, MP3)

================================================================================
For more information, see the README.md files in:
  - ../acoustic_privacy/README.md
  - ../content_privacy/README.md
  - ../README.md (main documentation)
================================================================================
