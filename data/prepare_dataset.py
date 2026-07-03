"""
Builds a synthetic training dataset for Indian fraud SMS/message classification.
Labels: digital_arrest, kyc_scam, investment_fraud, safe
Outputs: data/fraud_dataset.json, data/train.csv, data/test.csv
"""

import json
import random
import csv
import os
from pathlib import Path
from collections import Counter

random.seed(42)

# ---------------------------------------------------------------------------
# Synthetic message corpora
# ---------------------------------------------------------------------------

DIGITAL_ARREST_MESSAGES = [
    # English
    "This is Officer Sharma from CBI Delhi. Your Aadhaar number has been linked to illegal money laundering activities. You are under digital arrest. Do not disconnect this call.",
    "TRAI Notice: Your mobile number +91{phone} has been used for illegal activities. It will be disconnected in 2 hours unless you verify immediately. Call 1800-XXX-XXXX now.",
    "ED Office Mumbai: Rs 2.3 crore has been laundered using your bank account. A warrant is being issued. Cooperate now or face immediate arrest. This is your final warning.",
    "Customs Department: An illegal parcel in your name containing drugs and fake currency has been seized at Mumbai airport. You must appear before officials or face digital arrest.",
    "CBI notice: Your PAN card number {pan} has been used in 14 illegal transactions. Pay Rs 85,000 security deposit to avoid arrest. Contact officer immediately.",
    "This is DCP Verma from Cyber Crime Cell. Your IP address has been flagged for child trafficking content. You are digitally arrested. Do not move or contact anyone.",
    "ENFORCEMENT DIRECTORATE: Case number ED/MH/2024/{num} has been filed against you. Your assets will be frozen. Call our officer within 1 hour to provide clarification.",
    "Supreme Court Bench: You have been found guilty in absentia. Pay Rs 1,50,000 bail amount digitally to avoid physical custody. Court order number SC-{num}.",
    "Narcotics Control Bureau: A drug consignment worth Rs 18 crore was found linked to your Aadhaar. Senior officer Ramesh Kumar will call you. Do not contact police.",
    "This is IPS officer Anil Singh from Delhi Police Cyber Cell. Your WhatsApp has been used to send terrorist content. You are under surveillance. Stay connected.",
    "Income Tax Department: You have evaded tax worth Rs 43 lakhs. A raid is being planned at your address. To settle this matter, transfer Rs 2 lakhs as security.",
    "TRAI Alert: 6 complaints have been filed against your number for fraud calls. Your number will be permanently blocked in 24 hours. Press 1 to speak with an officer.",
    "CBI Officer Pradeep Mishra: We have evidence of your involvement in the {num} crore scam. A non-bailable warrant has been issued. Call us before 5 PM today.",
    "Fake courier: Your parcel from Hong Kong has been intercepted at IGI Airport. It contains 2 kg narcotics. Pay customs duty of Rs 1,20,000 or face arrest.",
    "Department of Telecom: Your SIM card linked to Aadhaar {aadhaar} is being misused. All services will be suspended. Verify identity with officer Sharma.",
    # Hinglish
    "Aapka Aadhaar number illegal activities mein use hua hai. Aap digital arrest mein hain. Call mat katna warna seedha police aayegi ghar pe.",
    "Sir, main CBI officer Rajesh hun. Aapke account se Rs 45 lakh transfer hue hain foreign accounts mein. Abhi cooperate karo nahi toh warrant issue hoga.",
    "TRAI se call hai. Aapka number 2 ghante mein band ho jayega kyunki aap fraud activities mein shamil hain. Abhi 1800 number pe call karo.",
    "Aap digital girftaar hain. Koi bhi family member ko mat batana. Court ke samne virtual tarike se pesh hona hoga. Officer aapko guide karenge.",
    "Customs ka notice hai. Mumbai airport pe aapke naam ka parcel pakda gaya hai jisme cash aur drugs hain. Rs 75,000 fine do warna FIR hogi.",
    "ED se strict notice: Aapke bank account mein suspicious transactions mile hain. 1 ghante mein humse contact karo nahi toh property attach ho jayegi.",
    "Aap par cybercrime ka case darj hua hai. IPS Sharma sahib aapki baat karna chahte hain. Call mat katna ye aapke haq mein nahi hoga.",
    "CBI Mumbai: Aapke PAN card se 7 fake companies register hui hain. Tune ye kiya hai? Sach batao ya jail jaoge. Abhi respond karo.",
    "Tera Aadhaar card hawala transactions mein use hua. NCB officer yahan se investigate kar raha hai. Tu seedha phas gaya hai. Cooperate kar.",
    "RBI ka notice: Aapka account money laundering mein involve paya gaya hai. 2 lakh security deposit jama karo nahi toh account freeze.",
    # Hindi (Devanagari)
    "यह सीबीआई अधिकारी शर्मा हैं। आपका आधार नंबर अवैध गतिविधियों में उपयोग किया गया है। आप डिजिटल गिरफ्तारी में हैं।",
    "ट्राई नोटिस: आपका मोबाइल नंबर 2 घंटे में बंद हो जाएगा। तुरंत अधिकारी से संपर्क करें।",
    "प्रवर्तन निदेशालय: आपके बैंक खाते से करोड़ों रुपये की हेराफेरी हुई है। तुरंत हमसे संपर्क करें।",
    "कस्टम विभाग: मुंबई एयरपोर्ट पर आपका पार्सल जब्त हुआ है। 1,20,000 रुपये का जुर्माना भरें।",
    "सुप्रीम कोर्ट का आदेश: आपके खिलाफ वारंट जारी हुआ है। तुरंत ऑनलाइन पेश हों।",
    "नारकोटिक्स ब्यूरो: आपके नाम पर ड्रग्स का कंसाइनमेंट पकड़ा गया। अभी अधिकारी से बात करें।",
    "आयकर विभाग: आपने 43 लाख की टैक्स चोरी की है। 2 घंटे में सिक्योरिटी राशि जमा करें।",
    "दिल्ली पुलिस साइबर सेल: आपका IP एड्रेस संदिग्ध गतिविधियों से जुड़ा है। कॉल न काटें।",
    # Kannada
    "ಸಿಬಿಐ ಅಧಿಕಾರಿ ಶರ್ಮಾ ಅವರಿಂದ: ನಿಮ್ಮ ಆಧಾರ್ ನಂಬರ್ ಅಕ್ರಮ ಚಟುವಟಿಕೆಗಳಲ್ಲಿ ಬಳಸಲಾಗಿದೆ. ನೀವು ಡಿಜಿಟಲ್ ಬಂಧನದಲ್ಲಿದ್ದೀರಿ.",
    "ಟ್ರಾಯ್ ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ಮೊಬೈಲ್ ನಂಬರ್ 2 ಗಂಟೆಯಲ್ಲಿ ಸ್ಥಗಿತಗೊಳ್ಳುತ್ತದೆ. ತಕ್ಷಣ ಸಂಪರ್ಕಿಸಿ.",
    "ಜಾರಿ ನಿರ್ದೇಶನಾಲಯ: ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯಲ್ಲಿ ಅನುಮಾನಾಸ್ಪದ ವ್ಯವಹಾರಗಳು ಪತ್ತೆಯಾಗಿವೆ.",
    # More English variants with typos and urgency
    "URGENT: CBI offiicer here. Your Aadhar is linked 2 drug traffiking ring. Plz dont disconect. You will be put under digitl arrest.",
    "This is offcer Suresh frm Enforcement Directorte. Rs 89 lakhs laundered thru ur account. Cooperate or warrent issued 2day.",
    "TRAI final warning!! Ur number reporting for fraud activties. Disconnection in 1 hr. Call immeditly on officer numer.",
    "Custms dept: ilegal parcel seized ur name. Ipd drugs + USD 50000 cash. Pay Rs 1.5L fine online OR face non-bailble arrest.",
    "CBI notice: 17 fake bank accnts opend using ur PAN. Warrent ready. Last chance - call offcr Pandey b4 6pm 2day.",
    # More variations
    "Your Aadhaar has been suspended due to suspicious activity. An FIR will be filed within 2 hours. Officer Mehra is trying to reach you. Pick up immediately.",
    "Mumbai Crime Branch: We have your IP logs. Child exploitation material traced to your device. This is a non-bailable offense. Cooperate to avoid physical arrest.",
    "This is a court summons. You are required to appear virtually before the magistrate in 30 minutes regarding money laundering charges. Do not ignore.",
    "RBI Fraud Department: Your account XXXX{num} has been used for illegal forex transactions. Account frozen pending investigation. Contact officer to unfreeze.",
    "CYBER POLICE: Your mobile is being used as a node in a ransomware attack on government servers. You are complicit. Cooperate with officer Agarwal immediately.",
    # Hinglish with different structure
    "Bhai sun, main Rajesh bol raha hun CBI se. Teri bahut badi gadbad hai. 2 crore ka mamla hai. Abhi baat karte hain warna problem hogi.",
    "Memsaab, aapke naam pe fraud case hai. Main Sharma officer hun. Family ko mat batana. Hamse seedha deal karo, settle ho jayega.",
    "Sir aapka phone number terrorist activities me linked hai Pakistan connection ke saath. Abhi verify karo nahi toh NIA aayegi ghar.",
    "Aapka Aadhaar use karke kisi ne 14 sim cards nikale hain. Ye sim Jammu-Kashmir mein illegal kaam mein use ho rahe hain. Abhi action lo.",
    # Formal English
    "Notice from the Directorate of Revenue Intelligence: Shipment containing contraband items bearing your identity proof has been intercepted. Immediate clarification required.",
    "Office of the Commissioner of Customs: It has come to our notice that you are the consignee of an illegal international package. Report to our virtual office immediately.",
    "Central Bureau of Investigation, New Delhi: This is to inform you that Case No. CBI/DEL/2024/{num} has been registered against your name. Compliance is mandatory.",
    "Ministry of Finance Alert: Tax evasion of Rs {num} lakhs detected in your name. File an explanation within 1 hour or automatic arrest warrant will be generated.",
    "Interpol has flagged your financial transactions as suspicious. Indian authorities have been notified. You have 1 hour to contact the assigned officer.",
    # More Hinglish and Hindi variants
    "Dekho bhai, tumhare upar serious charge hai. CBI ka case number hai {num}. Agar tum abhi cooperate nahi karte toh tumhara family bhi involve ho sakta hai.",
    "Aapki beti/beta ke naam pe bhi case darj ho sakta hai agar aap cooperate nahi karte. Officer sahib bahut patient hain abhi. Jaldi faisla karo.",
    "Main NCB ka officer hun. Tere phone pe drug dealer ke messages hain. Tune unhe reply kiya hai. Ye crime hai. Abhi settle karo.",
    "आपका SIM card drug traffickers को बेचा गया था। आपका नाम FIR में है। अभी हमारे अधिकारी से बात करें।",
    "TRAI strict action: Multiple fraud complaints against ur no. Last warning before permanent disconnection. Speak to nodal officer NOW.",
    "You are accused of operating a fake call center from your home. Evidence collected. CBI team en route. Cooperate or face arrest.",
    # Short variants
    "Digital arrest - CBI. Aadhaar fraud case. Do not hang up.",
    "ED notice: money laundering. Cooperate or warrant issued today.",
    "TRAI: number disconnect in 1 hr. Call officer immediately.",
    "Customs seized parcel. Your name. Drugs found. Pay fine now.",
    "Income Tax raid planned. Settle now. Rs 2L security deposit.",
    "NCB case filed against you. Drug trafficking. Cooperate.",
    "आप डिजिटल गिरफ्तारी में हैं। कॉल मत काटें।",
    "ನೀವು ಡಿಜಿಟಲ್ ಬಂಧನದಲ್ಲಿದ್ದೀರಿ. ಕರೆ ತಪ್ಪಿಸಿಕೊಳ್ಳಬೇಡಿ.",
    "Aap digital arrest mein hain. Phone mat kato.",
    "CBI officer calling. Stay on line. Do not inform family.",
    # Additional variety
    "Your Aadhaar-linked SIM is involved in distributing obscene content. Section 67 of IT Act is applicable. Officer will call you in 5 minutes.",
    "IMPORTANT: IB (Intelligence Bureau) has placed your number under surveillance. Unusual financial transactions detected. This is classified. Do not discuss with anyone.",
    "Court order No. HC/DEL/2024/{num}: You are summoned via video conference for a hearing related to financial fraud. Non-appearance will result in immediate arrest.",
    "Beware: Your UPI ID {upi} has been flagged for suspicious transactions by RBI. Temporary suspension imposed. Verify identity with assigned officer to restore.",
    "Interpol Red Notice issued against you in connection with online fraud ring. Indian CBI collaborating. Contact assigned liaison officer within 2 hours.",
    "Officer Priya Sharma from Delhi Cyber Crime: We have traced multiple fraudulent transactions to your device IMEI. You have the right to remain silent but must cooperate.",
    "Aapka naam hawala network mein aaya hai. Dubai se transaction hua Rs 78 lakh. Name aur PAN match hua aapka. Ye serious hai. Officer call karega.",
    "आपके आधार नंबर पर 9 शिकायतें दर्ज हैं। आपका खाता कल तक बंद हो जाएगा। अभी अधिकारी से संपर्क करें।",
]

KYC_SCAM_MESSAGES = [
    # English - Bank KYC
    "Dear Customer, your SBI account XXXX{num} will be blocked today. Complete KYC immediately: bit.ly/sbi-kyc{num}. Ignore at your own risk.",
    "HDFC Bank Alert: Your account will be suspended in 24 hours due to incomplete KYC. Update now: http://hdfc-kyc.{domain}.com",
    "Your Axis Bank account has been flagged. Incomplete KYC verification. Click to update: axisbank-kyc.{domain}.in or call 1800-XXX-XXXX",
    "PNB Notice: KYC documents not received. Account will be frozen by midnight. Upload docs at pnb.{domain}.com immediately.",
    "ICICI Bank: Urgent KYC update required. Your debit card and net banking will be suspended within 2 hours. Update now via the link below.",
    "BOI (Bank of India) Alert: Your savings account KYC is expired. Last date today. Click here to renew KYC online or visit branch.",
    "Kotak Mahindra Bank: We notice your KYC is incomplete. To avoid account suspension, verify at kotak-ekyc.{domain}.in",
    "Yes Bank KYC: Your account is at risk. Provide Aadhaar OTP verification immediately. Ignore this at risk of losing all balance.",
    "Union Bank of India: As per RBI mandate, KYC update is compulsory. Failure to comply will result in account freeze. Update now.",
    "Canara Bank customer, your KYC is pending since 6 months. Account will be suspended tomorrow. Call 1800-425-0018 (fake) or click link.",
    # English - OTP fraud
    "Your OTP for SBI net banking is 847293. Do NOT share with anyone. SBI never asks for OTP. (Note: scammer will follow up asking for this OTP)",
    "Paytm KYC: Your account is at risk of suspension. Share the OTP sent to your number to complete full KYC with our agent.",
    "PhonePe Security Alert: Unauthorized login attempt detected. Share OTP 567834 with our security executive to block this attempt.",
    "Google Pay verification: Your UPI handle needs re-linking. Agent will call you. Share OTP to verify. Do not close this message.",
    "Your Amazon Pay wallet will be deactivated. OTP for re-verification: 723948. Share with Amazon agent on call to restore wallet.",
    "BHIM UPI: KYC expiry alert. Your UPI ID {upi} will be deactivated. OTP being sent. Share with helpdesk agent immediately.",
    "Dear customer, your Mobikwik account will be closed. KYC not updated. Please share the OTP you receive to our helpdesk agent.",
    "RuPay card verification: Your card linked to account will stop working. Share OTP with bank executive calling you now.",
    # English - UIDAI/Aadhaar
    "UIDAI Alert: Your Aadhaar {aadhaar} has been used 13 times in last 24 hours. Suspicious activity detected. Verify at uidai-verify.{domain}.com",
    "Aadhaar Update: Your mobile number is not linked with Aadhaar. Account benefits will stop. Link now at uidai.{domain}.in/link",
    "UIDAI: Your Aadhaar biometric is locked. Unlock it by visiting uidai-{domain}.com and entering OTP. Urgent action required.",
    "Your Aadhaar has been blocked by UIDAI due to suspicious usage. Unblock online at fake link or call 1947-XXX-XXXX immediately.",
    # Hinglish
    "Bhai aapka SBI account kal tak block ho jayega. KYC nahi hua. Abhi is link pe click karo: sbi-{domain}.com/kyc",
    "Paytm se message: Aapka account suspend ho raha hai. KYC poora karo. OTP share karo humare agent ke saath.",
    "HDFC Bank: Aapki KYC expire ho gayi hai. Aaj raat 12 baje se account freeze. Abhi update karo.",
    "Aapka Aadhaar UIDAI ne block kar diya hai. Benefits ruk jayenge. Turant verify karo is link pe.",
    "PhonePe account mein problem hai. Agent call karega. OTP share karna hoga account activate karne ke liye.",
    "Aapka bank account mein suspicious activity pata chali hai. OTP se verify karo turant warna account band.",
    "UPI ID band hone wala hai. KYC update karo. Agent aapko call karega. Unhe OTP dedo.",
    "Aapke debit card ki validity khatam ho rahi hai. Nayi card ke liye OTP share karo humse.",
    "SBI Zero Balance account: Aapki KYC nahi hui. Rs 500 fine lagega. Abhi update karo.",
    "Jio SIM card band hona wala hai KYC ke bina. Abhi is link pe jao aur Aadhaar OTP dalo.",
    # Hindi (Devanagari)
    "आपका SBI खाता आज बंद हो जाएगा। KYC अपडेट करें: sbi-kyc.{domain}.in",
    "HDFC बैंक: आपकी KYC अधूरी है। 24 घंटे में खाता फ्रीज़ होगा।",
    "पेटीएम अलर्ट: आपका खाता निलंबित होने वाला है। KYC पूरा करें।",
    "UIDAI: आपका आधार संदिग्ध गतिविधि के कारण ब्लॉक किया गया है।",
    "आपके UPI ID की KYC समाप्त हो गई है। तुरंत अपडेट करें।",
    "RBI निर्देश: सभी ग्राहक 30 नवंबर से पहले KYC अपडेट करें।",
    "आपका डेबिट कार्ड ब्लॉक होने वाला है। OTP एजेंट को दें।",
    "बैंक ऑफ बड़ौदा: KYC अधूरी होने के कारण आपका खाता फ्रीज़ होगा।",
    # Kannada
    "ನಿಮ್ಮ SBI ಖಾತೆ ನಾಳೆ ಬ್ಲಾಕ್ ಆಗುತ್ತದೆ. KYC ಅಪ್ಡೇಟ್ ಮಾಡಿ.",
    "HDFC ಬ್ಯಾಂಕ್: ನಿಮ್ಮ KYC ಅಪೂರ್ಣವಾಗಿದೆ. ತಕ್ಷಣ ನವೀಕರಿಸಿ.",
    "Paytm ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ಖಾತೆ ಅಮಾನತುಗೊಳ್ಳುತ್ತಿದೆ. KYC ಮಾಡಿ.",
    "ಆಧಾರ್ ಅಪ್ಡೇಟ್: ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಲಿಂಕ್ ಆಗಿಲ್ಲ. ತಕ್ಷಣ ಲಿಂಕ್ ಮಾಡಿ.",
    "ನಿಮ್ಮ UPI KYC ಅವಧಿ ಮೀರಿದೆ. ನವೀಕರಣಕ್ಕಾಗಿ OTP ಹಂಚಿಕೊಳ್ಳಿ.",
    # More English variants with typos
    "Ur SBI accnt wil b blokd 2morrow. KYC not cmpletd. Updt NOW: sbi-{domain}.in/kyc or cal 1800XXXXXX",
    "URGENT!! Ur Paytm a/c suspndd. KYC expird. Snd OTP 2 our agnt to reactivte. Do NOT delay.",
    "PhonePe alrt: Suspcious lgn 2 ur accnt frm unknwn device. Vrfy by shrng OTP with scrity team.",
    "Ur HDFC net baking acss will stop 2nite. KYC docmnts not recvd. Submt at hdfc-{domain}.com",
    "Amaazn Pay: ur walleet balnce at risk. KYC vrification pendng. Agnt wil cal u. Share OTP.",
    # More diverse examples
    "MOBIKWIK: Your account shows irregular transactions. For security, verify your identity by sharing the OTP our agent will ask for.",
    "Dear {name} ji, your Jio SIM will be deactivated as Aadhaar KYC not completed. Link at jio.{domain}.com/kyc today.",
    "Ola Money Wallet: KYC incomplete. Wallet will be suspended. Complete via Aadhaar OTP verification with our agent.",
    "Flipkart Pay Later: Your BNPL account needs KYC update as per RBI guidelines. Update by today or service suspended.",
    "Your IRCTC account needs re-KYC as per new railway guidelines. Verify at irctc-{domain}.com or lose booking history.",
    "Airtel Payment Bank: Complete your Video KYC in 24 hours or your account will be downgraded. Share OTP to initiate.",
    "Vodafone-Idea: Your prepaid account needs Aadhaar re-verification. OTP will be sent. Share with our agent to verify.",
    "BSNL SIM: Mandatory KYC update pending. SIM will deactivate in 48 hours. Visit store or complete online with OTP.",
    # Short urgent variants
    "SBI KYC update karo aaj, account block ho jayega.",
    "Paytm account suspend - share OTP with agent to activate.",
    "HDFC bank KYC urgent - 24 hrs mein update nahi hua toh freeze.",
    "OTP share karo agent ke saath - UPI re-verify karna hai.",
    "ಅರ್ಜೆಂಟ್: SBI KYC ಅಪ್ಡೇಟ್ ಮಾಡಿ, ನಾಳೆ ಬ್ಲಾಕ್.",
    "आपका खाता बंद होगा। KYC करें।",
    "Your bank acct will b blocked. Update KYC now.",
    "Send OTP 2 verify ur Paytm - agent calling now.",
    # NPCI / RBI themed
    "NPCI Notice: Your UPI registration has expired. Re-register via OTP. Agent will assist. Do not share with others except our agent.",
    "RBI Mandate: All UPI users must complete annual KYC by month end. Share Aadhaar OTP with assigned bank executive.",
    "Your Rupay card linked to {name}'s account will stop working Dec 31. KYC update required. Call 1800-XXX-XXXX immediately.",
    # Additional Hinglish
    "Ek baar OTP share karo, main aapki problem solve kar deta hun 2 minute mein. Bank agent hun main.",
    "Aapki problem mujhe pata hai. OTP doge toh main direct aapka account thik kar dunga. Trust karo.",
    "Main aapke bank se bol raha hun. Aapka account mein kuch problem hai. OTP se verify karo abhi.",
    "Aapka Aadhaar lock hua hua hai. Main UIDAI se hun. OTP doge toh main unlock kar dunga.",
    "Aapka Jio SIM band hoga kal. Abhi OTP doge toh main process kar lunga. Quick rehna.",
]

INVESTMENT_FRAUD_MESSAGES = [
    # English
    "Earn Rs 50,000 per day from home! No experience needed. Join our exclusive WhatsApp group for stock tips that guarantee 200% returns. Limited seats!",
    "Bitcoin investment opportunity! Double your money in 7 days. Our AI trading bot has 98% success rate. Invest Rs 10,000 get Rs 20,000 in a week. WhatsApp: +91{phone}",
    "SEBI registered advisor {name} is sharing FREE stock tips this week. His last 10 calls gave 300% returns. Join now: t.me/stocktips{num}",
    "Mutual Fund alternative: Our P2P lending platform gives 36% annual returns. RBI regulated. Minimum Rs 5000. Zero risk. Join 50,000 happy investors.",
    "MLM opportunity: Join our herbal product network and earn Rs 2 lakhs monthly. Work from home. Be your own boss. Training provided free.",
    "Crypto pump alert: XYZ coin will 10x in 48 hours. Inside information from exchange insiders. Buy now before price jumps. Telegram: @cryptopump{num}",
    "Work from home: Like YouTube videos and earn Rs 1000 per hour. Part time job. No investment needed. {num} people already earning. Join now!",
    "NIFTY sure shot calls: Today's tip - Buy Reliance @ 2400, target 2700 in 3 days. 95% accuracy. Free trial for 7 days. WhatsApp JOIN to +91{phone}",
    "Referral program: Refer 5 friends and earn Rs 5000. No product selling. Just share links. Trusted by 1 lakh Indians. App download: {domain}.apk",
    "Forex trading: Learn and earn from international currency markets. Our expert traders make Rs 3-5 lakh monthly. Weekend workshop Rs 999 only.",
    "Option trading tips: Get daily 3-5 sure shot calls. SEBI registered. Last month 28 out of 30 calls were profitable. Subscribe now Rs 2999/month.",
    "Real estate investment: 24% guaranteed returns on commercial property fractional ownership. Starting Rs 25,000. RERA approved projects. Call now.",
    "Gold investment scheme: Deposit Rs 1000 monthly for 24 months. Get 30% bonus at maturity. Backed by physical gold reserves. Chit fund alternative.",
    "Online trading academy: Learn to make Rs 10,000/day from stock market. 3-day workshop by IIM alumni. Batch starting this weekend. Seats filling fast.",
    # Hinglish
    "Bhai ek baar try karo is scheme ko. Rs 10,000 lagao, 30 din mein double. Maine khud kiya hai. Ye scam nahi hai. Pakka.",
    "Mere paas ek insider tip hai. Kal subah ye stock 40% jump karega. Abhi buy karo. Kal profit enjoy karo. WhatsApp pe join karo.",
    "Ghar baithe paise kamao! YouTube pe video like karo, Rs 500 pratidin milenge. 5000 log already kar rahe hain ye kaam.",
    "Bitcoin double scheme: Rs 50,000 invest karo, 15 din mein Rs 1 lakh milega. Guaranteed. Mere 20 doston ne kiya hai.",
    "MLM plan: Rs 5000 invest karo, 5 logo ko join karo, har mahine Rs 25,000 aao gharbaithe. Network marketing.",
    "Share market mein sahi guide chahiye? Mera group join karo. Free tips deta hun. Pichle mahine 15 calls mein 12 profit mein.",
    "Crypto trading seekho aur Rs 2 lakh mahina kamao. 3 din ka course Rs 1999 mein. Certified trainer se sikhega.",
    "Online paise kamane ka best tarika: Affiliate marketing. Rs 3 lakh monthly possible. Free training kal shaam 6 baje Zoom pe.",
    # Hindi (Devanagari)
    "रोज़ 50,000 कमाओ घर बैठे! हमारे WhatsApp ग्रुप से जुड़ें। 100% गारंटी।",
    "बिटकॉइन में निवेश करें। 7 दिन में पैसे दोगुने। AI ट्रेडिंग बॉट।",
    "SEBI रजिस्टर्ड एडवाइजर: फ्री स्टॉक टिप्स के लिए जुड़ें। 200% रिटर्न।",
    "घर से काम करें। यूट्यूब वीडियो लाइक करें। रोज़ Rs 1000 कमाएं।",
    "क्रिप्टो पंप: XYZ कॉइन 48 घंटे में 10x होगा। अभी खरीदें।",
    "म्यूचुअल फंड से ज़्यादा रिटर्न! हमारी P2P स्कीम में 36% सालाना।",
    # Kannada
    "ಮನೆಯಿಂದ ₹50,000 ದಿನಕ್ಕೆ ಗಳಿಸಿ! ನಮ್ಮ WhatsApp ಗ್ರೂಪ್ ಸೇರಿ.",
    "Bitcoin ಹೂಡಿಕೆ: 7 ದಿನಗಳಲ್ಲಿ ಹಣ ದ್ವಿಗುಣ. AI ಟ್ರೇಡಿಂಗ್ ಬಾಟ್.",
    "ಷೇರು ಮಾರುಕಟ್ಟೆ ಟಿಪ್ಸ್: ಪ್ರತಿ ದಿನ ₹10,000 ಸಂಪಾದಿಸಿ.",
    # More English with urgency/fake legitimacy
    "SEBI Certified Advisor Alert: STRONG BUY on XYZ stock. Target Rs 450 from current Rs 300. Time sensitive. Act within 2 hours.",
    "NSE/BSE listed company pre-IPO shares available at 40% discount. Guaranteed listing gains. Limited allocation. Minimum Rs 50,000.",
    "Telegram signal group made 140% returns last month. Verified track record. Join now: t.me/niftymaster{num}. Free for 7 days.",
    "International forex arbitrage: Risk-free profit guaranteed. Our algorithm exploits price differences across markets. Min investment $500.",
    "PUMP ALERT: Penny stock ready to explode. Buy before institutional investors. Inside info from market operator. Telegram now.",
    "Network marketing: 3 levels of income. Sell wellness products + recruit = Rs 1-5 lakh monthly. Top earners are proof. Join free.",
    "Earn from Google: Work as online ad evaluator. Rs 25-40/hour. Work from home. No experience. Apply at google-jobs-{domain}.com",
    "Fixed deposit alternative: 18% annual return. Better than bank FD. Secured against real estate collateral. NBFC registered.",
    "Quick money: Complete simple tasks online. Data entry, surveys, clicking ads. Rs 500-2000 daily. Register at tasks-{domain}.com",
    "Agri commodity tips: Soy, wheat, gold futures - daily calls. Agri markets less risky than equity. Join our expert group now.",
    # Short variants
    "Earn 50k/day from home. WhatsApp: +91{phone}",
    "Bitcoin double in 7 days. Invest now. 98% success rate.",
    "Free stock tips. Join group. 200% returns guaranteed.",
    "MLM: Rs 25,000/month ghar baithe. 5 log join karo.",
    "Crypto pump 48 hrs. 10x guaranteed. Telegram now.",
    "ಮನೆಯಿಂದ ₹50,000 ಗಳಿಸಿ. WhatsApp ಸೇರಿ.",
    "रोज़ 50,000 कमाओ। गारंटी।",
    # Task-based fraud
    "Part time job from home: Rate hotels on Google Maps. Rs 150-300 per review. 10-20 reviews daily. Earn Rs 3000/day. Apply now.",
    "Typing job: Type 100 words = Rs 500. Work from home. No experience needed. Earn Rs 15,000 monthly. Genuine company hiring.",
    "Photo editing online job: Edit 10 photos, earn Rs 1500. Work from home. Training provided. Apply at editjobs-{domain}.com",
    "Telegram channel moderator job: Rs 800/hour. Part time. Work from phone. No experience. Apply and start tomorrow.",
]

SAFE_MESSAGES = [
    # Bank OTPs (real)
    "Your OTP for SBI net banking login is 847293. Valid for 10 minutes. Do not share with anyone. -SBI",
    "HDFC Bank: OTP for transaction of Rs 1,250 at Amazon.in is 392847. Valid 5 mins. Do not share. -HDFC",
    "Your ICICI Bank OTP is 671829 for UPI payment of Rs 500 to {upi}. Valid for 5 mins.",
    "Axis Bank: OTP 234891 for net banking login from IP 103.XXX.XXX. Valid 10 mins. Do not share. -Axis",
    "Kotak Bank OTP: 918273 for IMPS transfer of Rs 10,000. Do not share this OTP with anyone.",
    "Your OTP for PayTM transaction is 546372. Never share OTP with anyone, not even Paytm. -Paytm",
    "PhonePe: OTP 892341 for payment of Rs 2,500. Do not share with anyone. Report fraud: 08068727374",
    "Google Pay: Your OTP is 763829. Never share this with anyone including Google staff.",
    "Amazon Pay OTP: 234765 for Rs 3,499 purchase. Valid 10 mins. Amazon never asks for OTP on call.",
    "Flipkart: OTP 987234 for your order payment of Rs 1,799. OTP valid for 5 minutes.",
    # Delivery notifications
    "Your Flipkart order #FL{num}23 has been shipped. Expected delivery: {date}. Track: flipkart.com/orders",
    "Amazon delivery: Your order will arrive today by 8 PM. Your package is with delivery partner Rahul.",
    "Meesho order dispatched. Estimated delivery in 3-5 days. Track your order at meesho.com",
    "Myntra: Your order for Puma T-Shirt (Size L) has been delivered at your doorstep. Rate your experience.",
    "Swiggy: Your food from {restaurant} is being prepared. Delivery partner will pick up in 10 mins.",
    "Zomato order confirmed. Estimated delivery 35-40 minutes. Order ID: ZOM{num}",
    "DTDC tracking: Your courier {num} has been delivered. Received by: Rajesh. Time: 2:45 PM",
    "BlueDart: Package AWB{num} out for delivery today. Contact 1860-233-1234 for queries.",
    "Delhivery: Shipment {num} reaching you today. Available between 10 AM - 7 PM.",
    "Ekart: Your Flipkart package is 5 stops away. Approx 30 mins.",
    # Government real notifications
    "Your Aadhaar update request has been processed. UIDAI Reference: {num}. Download updated Aadhaar at myaadhaar.uidai.gov.in",
    "DigiLocker: Your document PAN Card has been fetched successfully and stored in your DigiLocker.",
    "ITR filing confirmation: Your Income Tax Return for AY 2024-25 has been filed. Acknowledgment no: {num}",
    "EPFO: Your PF withdrawal of Rs 45,000 has been approved. Amount will be credited to your bank in 3-5 days.",
    "PM-KISAN: 15th installment of Rs 2,000 has been credited to your bank account linked with Aadhaar.",
    "Ayushman Bharat: Your card is ready. Collect from nearest CSC center with Aadhaar. Scheme No: AB-{num}",
    "CoWIN: Vaccine certificate for {name} has been updated. Download at cowin.gov.in. Booster reminder set.",
    "IRCTC: PNR {num} booked from Delhi to Mumbai on {date}. Seat: 3AC B2/34. Fare: Rs 1,245.",
    "Passport seva: Your passport application {num} has been dispatched by Speed Post. ETA 3-5 days.",
    "RTO: Vehicle registration certificate for MH-XX-{num} has been renewed successfully. Valid till {date}.",
    # Personal / transactional messages
    "Hi {name}, your appointment with Dr. Sharma is confirmed for tomorrow at 11 AM. Clinic: Apollo, Bangalore.",
    "Reminder: Your EMI of Rs 8,500 for home loan is due on 5th. Auto-debit set. Ensure sufficient balance. -HDFC",
    "Your credit card bill of Rs 23,456 is due on 20th Jan. Pay now to avoid late fee. -Axis Bank",
    "School fees reminder: Last date for {name}'s term 3 fees is 15th January. Amount: Rs 12,500.",
    "Society maintenance: January maintenance of Rs 3,500 due by 10th. Pay via UPI to society@upi",
    "Electricity bill: Your EB no {num} January bill amount is Rs 1,456. Due date 25th Jan. Pay at bescom.in",
    "Gas booking confirmed. Cylinder will be delivered tomorrow between 9 AM - 1 PM. Booking ref: {num}",
    "Your Airtel bill of Rs 499 is generated. Due date: 18th Jan. Pay via Airtel Thanks app or UPI.",
    "Jio recharge successful. New validity: 28 days. Data: 1.5GB/day. Balance: Rs 5. Recharge: Rs 239.",
    "Vodafone: Your international roaming is now active. Charges apply. Call 121 for rates.",
    # Hinglish personal
    "Kal milte hain? Main 6 baje free hun. Dinner pe chalo.",
    "Bhai kal match dekha? Kya game tha. India ne mara!",
    "Aaj office mein kya hua? Meeting kaisi rahi?",
    "Ghar aa raha hun 8 baje. Khana lao 2 plate extra.",
    "Happy Birthday {name}! Bhagwan aapko lambi umar de. Party kab hai?",
    "Kal subah 7 baje gym? Main aa raha hun. Confirm karo.",
    "Meeting 11 baje se shift ho gayi 3 baje. Calendar update karo.",
    "Kal report submit karni hai. Kya tumhari side se ready hai?",
    # Hindi (Devanagari) personal/official
    "आपका SBI खाते में Rs 15,000 जमा हुए। NEFT द्वारा। -SBI",
    "आपकी ITR फ़ाइल हो गई है। पावती संख्या: {num}",
    "IRCTC: PNR {num} बुक हुआ। दिल्ली से मुंबई। -IRCTC",
    "आपकी गैस बुकिंग हो गई। कल डिलीवरी होगी।",
    "EPF: आपकी निकासी स्वीकृत हुई। राशि 3-5 दिन में आएगी।",
    "कल मिलते हैं दोपहर 1 बजे? लंच पर चलते हैं।",
    "सोसाइटी मेंटेनेंस: जनवरी का Rs 3,500 15 तारीख से पहले दें।",
    "बिजली बिल: Rs 1,456 की राशि 25 जनवरी से पहले जमा करें।",
    # Kannada safe messages
    "ನಿಮ್ಮ SBI ಖಾತೆಗೆ Rs 15,000 ಜಮೆಯಾಗಿದೆ. -SBI",
    "IRCTC: PNR {num} ಬುಕ್ ಆಗಿದೆ. ಬೆಂಗಳೂರಿನಿಂದ ದೆಹಲಿ.",
    "ನಾಳೆ ಭೇಟಿಯಾಗೋಣ. ಮಧ್ಯಾಹ್ನ 1 ಗಂಟೆಗೆ ಊಟಕ್ಕೆ ಹೋಗೋಣ.",
    "ನಿಮ್ಮ Flipkart ಆರ್ಡರ್ ಇಂದು ಡೆಲಿವರಿ ಆಗುತ್ತದೆ.",
    "Jio ರೀಚಾರ್ಜ್ ಯಶಸ್ವಿ. ಮಾನ್ಯತೆ: 28 ದಿನಗಳು.",
    "ನಿಮ್ಮ ನೀರಿನ ತೆರಿಗೆ ಬಿಲ್ Rs 850. 20ನೇ ತಾರೀಕಿನ ಒಳಗೆ ಪಾವತಿಸಿ.",
    # More real-looking messages
    "Your CIBIL score has improved to 742. Check your full credit report at CIBIL.com. -TransUnion CIBIL",
    "LIC premium of Rs 12,500 received for policy {num}. Next due: 1st April 2025. -LIC of India",
    "NPS contribution of Rs 5,000 credited to your account for December 2024. PRAN: {num}.",
    "MF SIP of Rs 3,000 in HDFC Midcap Fund executed on 1st Jan. NAV: 52.34. Units: 57.26.",
    "Your FD of Rs 1 lakh matures on 15th March 2025. Auto-renewal at prevailing rate unless otherwise notified.",
    "Health check reminder: Your annual health checkup is due. Book at Apollo Diagnostics. 20% off this month.",
    "School result: {name} scored 89.4% in Class 10 boards. Rank 5 in school. Congratulations!",
    "Your Swiggy One subscription renewed for 3 months. Benefits: Free delivery, priority support. -Swiggy",
    "Traffic challan: Vehicle MH-XX-{num} was caught jumping red light at MG Road on {date}. Pay: echallan.parivahan.gov.in",
    "BMC Water Supply: Your area (Ward {num}) will have no water supply on Sunday from 8 AM to 2 PM due to maintenance.",
    # Professional messages
    "Hi team, tomorrow's standup is moved to 10 AM. Please join the usual Zoom link. -Project Manager Rahul",
    "Your leave application for Jan 15-17 has been approved. Enjoy your holiday! -HR, {company}",
    "Invoice #INV{num} from {company} for Rs 45,000. Due in 30 days. Bank transfer preferred.",
    "Your delivery to client {name} completed. Please rate the service: bit.ly/rate{num}",
    "Office will be closed on Republic Day (26th Jan). WFH optional for critical teams.",
    # Random personal
    "Main kal wapas aa raha hun. Ghar pe koi hai?",
    "Aaj ki meeting cancel ho gayi. Kal subah confirm karenge.",
    "{name}, aapki parcel kal subah 10 baje ayegi. Ghar pe rehna.",
    "Beta, khaana kha lena. Main 9 baje tak aaungi. -Mummy",
    "Sir, aapka car service complete ho gaya. Total: Rs 3,500. Collect kab karna hai?",
    "Tomar meeting 3pm naki 4pm? Confirm karo please. -Priya",
    "Happy Diwali! Subh Deepawali! May this festival bring joy and prosperity.",
    "Happy New Year 2025! Wishing you and your family a wonderful year ahead.",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INDIAN_NAMES = [
    "Rahul Sharma", "Priya Singh", "Amit Kumar", "Sunita Devi", "Rajesh Gupta",
    "Pooja Patel", "Suresh Nair", "Kavitha Reddy", "Vikram Joshi", "Anita Mehta",
    "Deepak Verma", "Meena Iyer", "Ravi Krishnan", "Seema Agarwal", "Sanjay Yadav",
    "Lakshmi Pillai", "Arun Bose", "Geeta Rao", "Manoj Tiwari", "Swati Malhotra",
    "Harish Gowda", "Rekha Naidu", "Prakash Hegde", "Usha Menon", "Kiran Patil",
    "Shobha Kulkarni", "Ramesh Shetty", "Nalini Desai", "Sunil Bhat", "Padma Nair",
]
RESTAURANTS = ["Meghana Foods", "MTR", "Karavalli", "Empire", "Domino's", "Pizza Hut", "Biryani Blues", "Haldiram's"]
DOMAINS = ["secure-verify", "bank-update", "kyc-portal", "verify-now", "account-secure", "ekyc-india"]
COMPANIES = ["TCS", "Infosys", "Wipro", "HCL", "Accenture", "Cognizant", "Tech Mahindra"]
DATES = ["15th Jan", "20th Feb", "5th Mar", "12th Apr", "28th May", "10th Jun"]


def fill_template(template: str) -> str:
    phone = "".join([str(random.randint(0, 9)) for _ in range(10)])
    pan = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000,9999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))}"
    aadhaar = f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
    name = random.choice(INDIAN_NAMES).split()[0]
    upi = f"{name.lower()}{random.randint(10,99)}@{random.choice(['oksbi','okaxis','paytm','ybl','upi'])}"
    num = str(random.randint(10000, 99999))
    domain = random.choice(DOMAINS)
    restaurant = random.choice(RESTAURANTS)
    date = random.choice(DATES)
    company = random.choice(COMPANIES)

    return (
        template
        .replace("{phone}", phone)
        .replace("{pan}", pan)
        .replace("{aadhaar}", aadhaar)
        .replace("{name}", name)
        .replace("{upi}", upi)
        .replace("{num}", num)
        .replace("{domain}", domain)
        .replace("{restaurant}", restaurant)
        .replace("{date}", date)
        .replace("{company}", company)
    )


def detect_language(text: str) -> str:
    devanagari = sum(1 for c in text if "ऀ" <= c <= "ॿ")
    kannada = sum(1 for c in text if "ಀ" <= c <= "೿")
    if devanagari > 5:
        return "hindi"
    if kannada > 5:
        return "kannada"
    hinglish_words = ["aap", "aapka", "karo", "hai", "hun", "nahi", "bhai", "mein", "ko", "se", "ka", "ki", "bata", "kya", "toh"]
    lower = text.lower()
    if sum(1 for w in hinglish_words if w in lower) >= 2:
        return "hinglish"
    return "english"


def build_corpus(templates, n_target):
    records = []
    pool = list(templates)
    while len(records) < n_target:
        t = random.choice(pool)
        records.append(fill_template(t))
    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base = Path(__file__).parent  # data/

    print("Generating synthetic Indian fraud message dataset ...")

    da_msgs = build_corpus(DIGITAL_ARREST_MESSAGES, 300)
    kyc_msgs = build_corpus(KYC_SCAM_MESSAGES, 300)
    inv_msgs = build_corpus(INVESTMENT_FRAUD_MESSAGES, 200)
    safe_msgs = build_corpus(SAFE_MESSAGES, 400)

    all_records = []
    for text in da_msgs:
        all_records.append({"text": text, "label": "digital_arrest", "language": detect_language(text)})
    for text in kyc_msgs:
        all_records.append({"text": text, "label": "kyc_scam", "language": detect_language(text)})
    for text in inv_msgs:
        all_records.append({"text": text, "label": "investment_fraud", "language": detect_language(text)})
    for text in safe_msgs:
        all_records.append({"text": text, "label": "safe", "language": detect_language(text)})

    random.shuffle(all_records)

    # Save JSON
    json_path = base / "fraud_dataset.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_records)} records to {json_path}")

    # Stratified 80/20 split
    by_label = {}
    for r in all_records:
        by_label.setdefault(r["label"], []).append(r)

    train_rows, test_rows = [], []
    for label, rows in by_label.items():
        random.shuffle(rows)
        split = int(len(rows) * 0.8)
        train_rows.extend(rows[:split])
        test_rows.extend(rows[split:])

    random.shuffle(train_rows)
    random.shuffle(test_rows)

    fieldnames = ["text", "label", "language"]
    train_path = base / "train.csv"
    test_path = base / "test.csv"

    for path, rows in [(train_path, train_rows), (test_path, test_rows)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # Print stats
    print("\n=== Dataset Statistics ===")
    label_counts = Counter(r["label"] for r in all_records)
    lang_counts = Counter(r["language"] for r in all_records)
    print(f"Total records : {len(all_records)}")
    print(f"Train size    : {len(train_rows)}")
    print(f"Test size     : {len(test_rows)}")
    print("\nLabel distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label:<20} {count}")
    print("\nLanguage distribution:")
    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang:<15} {count}")
    print(f"\nFiles saved:\n  {json_path}\n  {train_path}\n  {test_path}")


if __name__ == "__main__":
    main()
