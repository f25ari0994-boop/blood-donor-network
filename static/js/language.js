(function(){
"use strict";
const m=document.querySelector('meta[name="app-language"]');
const serverLang=m?m.content:"English";
const authenticated=!!(m&&m.dataset.authenticated==="true");
let lang=serverLang;
try{
  const saved=localStorage.getItem("app-language");
  if(authenticated){
    localStorage.setItem("app-language",serverLang);
  }else if(saved==="Urdu"||saved==="Sindhi"||saved==="English"){
    lang=saved;
  }
}catch(error){}
if(lang!=="Urdu"&&lang!=="Sindhi")return;
const D={
Urdu:{"Dashboard":"ڈیش بورڈ","Become a Donor":"خون کا عطیہ دہندہ بنیں","Find Donors":"عطیہ دہندگان تلاش کریں","Emergency Request":"ہنگامی درخواست","Donor Directory":"عطیہ دہندگان کی فہرست","Profile":"پروفائل","My Profile":"میری پروفائل","Notifications":"اطلاعات","Notification":"اطلاع","Logout":"لاگ آؤٹ","Log out":"لاگ آؤٹ","Home":"ہوم","About":"تعارف","How It Works":"طریقۂ کار","Login":"لاگ اِن","Signup":"سائن اَپ","My Matches":"میرے میچز","Available Blood Requests":"دستیاب خون کی درخواستیں","My Blood Requests":"میری خون کی درخواستیں","Create Blood Request":"خون کی درخواست بنائیں","Emergency Blood Requests":"ہنگامی خون کی درخواستیں","Edit Profile":"پروفائل میں ترمیم","My Donor Profiles":"میرے عطیہ دہندگان کے پروفائل","Language Preference":"زبان کی ترجیح","Save Changes":"تبدیلیاں محفوظ کریں","Update Profile":"پروفائل اپ ڈیٹ کریں","Cancel":"منسوخ کریں","Save":"محفوظ کریں","Submit":"جمع کریں","Search":"تلاش کریں","Filter":"فلٹر","Clear":"صاف کریں","View":"دیکھیں","View Donor Profile":"عطیہ دہندہ کی پروفائل دیکھیں","Open Dashboard":"ڈیش بورڈ کھولیں","Back to Dashboard":"ڈیش بورڈ پر واپس جائیں","Call":"کال کریں","WhatsApp":"واٹس ایپ","Chat":"چیٹ","Send":"بھیجیں","Close":"بند کریں","Name":"نام","Email":"ای میل","Phone":"فون","Location":"مقام","Hospital":"ہسپتال","Blood Group":"بلڈ گروپ","Units":"یونٹس","Units Needed":"درکار یونٹس","Units Received":"موصولہ یونٹس","Units Remaining":"باقی یونٹس","Urgency":"فوری نوعیت","Emergency":"ہنگامی","Normal":"عام","Status":"حیثیت","Date":"تاریخ","Time":"وقت","Deadline":"آخری وقت","Donation Date":"عطیہ کی تاریخ","Donation History":"عطیہ کی تاریخ","Report Donation":"عطیہ رپورٹ کریں","Confirm":"تصدیق کریں","Reject":"مسترد کریں","Accept":"قبول کریں","Available":"دستیاب","Not Available":"دستیاب نہیں","No Notifications Yet":"ابھی کوئی اطلاع نہیں","Contact details":"رابطے کی تفصیلات","Create your donor profile":"اپنا عطیہ دہندہ پروفائل بنائیں","Unknown":"نامعلوم","Blood Donor":"خون کا عطیہ دہندہ","Requester":"درخواست گزار","Donor":"عطیہ دہندہ","Required":"ضروری","Optional":"اختیاری","Loading...":"لوڈ ہو رہا ہے","No results found":"کوئی نتیجہ نہیں ملا","Please wait":"براہ کرم انتظار کریں","Personal Information":"ذاتی معلومات","Account Information":"اکاؤنٹ کی معلومات","Change Password":"پاس ورڈ تبدیل کریں","Password":"پاس ورڈ","Age":"عمر","Address":"پتہ","City":"شہر","Select":"منتخب کریں","No records found":"کوئی ریکارڈ نہیں ملا","No requests found":"کوئی درخواست نہیں ملی","No donors found":"کوئی عطیہ دہندہ نہیں ملا","My Requests":"میری درخواستیں","My Donations":"میرے عطیات","Donation":"عطیہ","Request":"درخواست","Requests":"درخواستیں","Donations":"عطیات","Receipt":"وصولی","Report":"رپورٹ","Today":"آج","All":"تمام","Unread":"غیر پڑھی ہوئی","Read":"پڑھی ہوئی","Send Message":"پیغام بھیجیں","Message":"پیغام","Messages":"پیغامات","Create Request":"درخواست بنائیں","Find Blood":"خون تلاش کریں","Donor Details":"عطیہ دہندہ کی تفصیلات","Request Details":"درخواست کی تفصیلات","Match Details":"میچ کی تفصیلات"},
Sindhi:{"Dashboard":"ڊيش بورڊ","Become a Donor":"رت جو عطيو ڏيندڙ بڻجو","Find Donors":"عطيو ڏيندڙ ڳوليو","Emergency Request":"هنگامي درخواست","Donor Directory":"عطيو ڏيندڙن جي فهرست","Profile":"پروفائل","My Profile":"منهنجو پروفائل","Notifications":"اطلاع","Notification":"اطلاع","Logout":"لاگ آئوٽ","Log out":"لاگ آئوٽ","Home":"گهر","About":"تعارف","How It Works":"ڪم ڪرڻ جو طريقو","Login":"لاگ اِن","Signup":"سائن اپ","My Matches":"منهنجا ميچ","Available Blood Requests":"رت جون موجود درخواستون","My Blood Requests":"منهنجون رت جون درخواستون","Create Blood Request":"رت جي درخواست ٺاهيو","Emergency Blood Requests":"هنگامي رت جون درخواستون","Edit Profile":"پروفائل ۾ ترميم","My Donor Profiles":"منهنجا عطيو ڏيندڙ پروفائل","Language Preference":"ٻولي جي ترجيح","Save Changes":"تبديليون محفوظ ڪريو","Update Profile":"پروفائل اپڊيٽ ڪريو","Cancel":"رد ڪريو","Save":"محفوظ ڪريو","Submit":"جمع ڪريو","Search":"ڳولا","Filter":"فلٽر","Clear":"صاف ڪريو","View":"ڏسو","View Donor Profile":"عطيو ڏيندڙ جو پروفائل ڏسو","Open Dashboard":"ڊيش بورڊ کوليو","Back to Dashboard":"ڊيش بورڊ ڏانهن واپس وڃو","Call":"ڪال ڪريو","WhatsApp":"واٽس ايپ","Chat":"چيٽ","Send":"موڪليو","Close":"بند ڪريو","Name":"نالو","Email":"اي ميل","Phone":"فون","Location":"هنڌ","Hospital":"اسپتال","Blood Group":"رت جو گروپ","Units":"يونٽ","Units Needed":"گهربل يونٽ","Units Received":"مليل يونٽ","Units Remaining":"باقي يونٽ","Urgency":"تڪڙ","Emergency":"هنگامي","Normal":"عام","Status":"حيثيت","Date":"تاريخ","Time":"وقت","Deadline":"آخري وقت","Donation Date":"عطئي جي تاريخ","Donation History":"عطئي جي تاريخ","Report Donation":"عطئي جي رپورٽ ڏيو","Confirm":"تصديق ڪريو","Reject":"رد ڪريو","Accept":"قبول ڪريو","Available":"موجود","Not Available":"موجود ناهي","No Notifications Yet":"اڃا تائين ڪو اطلاع ناهي","Contact details":"رابطي جا تفصيل","Create your donor profile":"پنهنجو عطيو ڏيندڙ پروفائل ٺاهيو","Unknown":"اڻڄاتل","Blood Donor":"رت جو عطيو ڏيندڙ","Requester":"درخواست ڪندڙ","Donor":"عطيو ڏيندڙ","Required":"ضروري","Optional":"اختياري","Loading...":"لوڊ ٿي رهيو آهي","No results found":"ڪو نتيجو نه مليو","Please wait":"مهرباني ڪري انتظار ڪريو","Personal Information":"ذاتي معلومات","Account Information":"اڪائونٽ جي معلومات","Change Password":"پاسورڊ تبديل ڪريو","Password":"پاسورڊ","Age":"عمر","Address":"پتو","City":"شهر","Select":"چونڊيو","No records found":"ڪو رڪارڊ نه مليو","No requests found":"ڪا درخواست نه ملي","No donors found":"ڪو عطيو ڏيندڙ نه مليو","My Requests":"منهنجون درخواستون","My Donations":"منهنجا عطيا","Donation":"عطيو","Request":"درخواست","Requests":"درخواستون","Donations":"عطيا","Receipt":"وصولي","Report":"رپورٽ","Today":"اڄ","All":"سڀ","Unread":"اڻپڙهيل","Read":"پڙهيل","Send Message":"پيغام موڪليو","Message":"پيغام","Messages":"پيغام","Create Request":"درخواست ٺاهيو","Find Blood":"رت ڳوليو","Donor Details":"عطيو ڏيندڙ جا تفصيل","Request Details":"درخواست جا تفصيل","Match Details":"ميچ جا تفصيل"}
};
const EXTRA = [
["Your Network, Your Impact","آپ کا نیٹ ورک، آپ کا اثر","توهان جو نيٽ ورڪ، توهان جو اثر"],
["Be part of a connected blood donation community. Manage your donor profile, find compatible donors and coordinate emergency blood requests through one platform.","خون کے عطیہ دہندگان کی مربوط کمیونٹی کا حصہ بنیں۔ اپنا ڈونر پروفائل منظم کریں، موزوں عطیہ دہندگان تلاش کریں اور ایک ہی پلیٹ فارم کے ذریعے ہنگامی خون کی درخواستوں کا انتظام کریں۔","رت جي عطيو ڏيندڙن جي گڏيل ڪميونٽي جو حصو بڻجو. پنهنجو ڊونر پروفائل سنڀاليو، مناسب عطيو ڏيندڙ ڳوليو ۽ هڪ ئي پليٽ فارم ذريعي هنگامي رت جي درخواستن جو انتظام ڪريو."],
["Quick Actions","فوری اقدامات","تڪڙا ڪم"],
["Choose what you want to do.","منتخب کریں کہ آپ کیا کرنا چاہتے ہیں۔","چونڊيو ته توهان ڇا ڪرڻ چاهيو ٿا."],
["Register / Manage Donor","عطیہ دہندہ کا اندراج / انتظام","عطيو ڏيندڙ جو اندراج / انتظام"],
["Create or update your donor profile, blood group and availability.","اپنا عطیہ دہندہ پروفائل، بلڈ گروپ اور دستیابی بنائیں یا اپ ڈیٹ کریں۔","پنهنجو عطيو ڏيندڙ پروفائل، رت جو گروپ ۽ دستيابي ٺاهيو يا اپڊيٽ ڪريو."],
["Search for compatible donors by blood group and location.","بلڈ گروپ اور مقام کے مطابق موزوں عطیہ دہندگان تلاش کریں۔","رت جي گروپ ۽ هنڌ موجب مناسب عطيو ڏيندڙ ڳوليو."],
["Create a new blood request and set the required blood group, location and needed-by deadline.","خون کی نئی درخواست بنائیں اور مطلوبہ بلڈ گروپ، مقام اور آخری وقت درج کریں۔","رت جي نئين درخواست ٺاهيو ۽ گهربل رت جو گروپ، هنڌ ۽ آخري وقت داخل ڪريو."],
["Explore registered donor profiles in the blood donor network.","بلڈ ڈونر نیٹ ورک میں رجسٹرڈ عطیہ دہندگان کے پروفائل دیکھیں۔","رت جي ڊونر نيٽ ورڪ ۾ رجسٽر ٿيل عطيو ڏيندڙن جا پروفائل ڏسو."],
["Every Drop Matters","خون کا ہر قطرہ قیمتی ہے","رت جو هر قطرو اهم آهي"],
["Keep your donor information and availability updated. The platform helps coordinate blood donation requests, while final donor suitability and transfusion decisions must always be confirmed by qualified healthcare professionals.","اپنی عطیہ دہندہ کی معلومات اور دستیابی اپ ڈیٹ رکھیں۔ یہ پلیٹ فارم خون کے عطیے کی درخواستوں میں رابطہ کاری کرتا ہے، جبکہ عطیہ دہندہ کی حتمی موزونیت اور انتقالِ خون کا فیصلہ مستند طبی ماہرین ہی کریں۔","پنهنجي عطيو ڏيندڙ جي معلومات ۽ دستيابي اپڊيٽ رکو. هي پليٽ فارم رت جي عطئي جي درخواستن ۾ سهڪار ڪري ٿو، جڏهن ته عطيو ڏيندڙ جي آخري موزونيت ۽ رت چاڙهڻ جو فيصلو ماهر طبي عملي کي ڪرڻ گهرجي."],
["Become a Blood Donor","خون کے عطیہ دہندہ بنیں","رت جو عطيو ڏيندڙ بڻجو"],
["Your willingness to donate may help someone in an emergency. Register your details so people searching for a matching blood group can find a potential donor.","آپ کا خون عطیہ کرنے کا ارادہ کسی ہنگامی صورتحال میں کسی کی مدد کر سکتا ہے۔ اپنی معلومات درج کریں تاکہ موزوں بلڈ گروپ تلاش کرنے والے افراد آپ کو ممکنہ عطیہ دہندہ کے طور پر تلاش کر سکیں۔","توهان جي رت عطيو ڪرڻ جي خواهش هنگامي حالت ۾ ڪنهن جي مدد ڪري سگهي ٿي. پنهنجا تفصيل داخل ڪريو ته جيئن مناسب رت جو گروپ ڳوليندڙ ماڻهو توهان کي ممڪن عطيو ڏيندڙ طور ڳولي سگهن."],
["Donor Registration","عطیہ دہندہ کا اندراج","عطيو ڏيندڙ جو اندراج"],
["Enter accurate information. Fields marked with","درست معلومات درج کریں۔ جن خانوں پر","صحيح معلومات داخل ڪريو. جن خانن تي"],
["are required.","کا نشان ہے وہ لازمی ہیں۔","جو نشان آهي، اهي لازمي آهن."],
["Donors must be at least 18 years old.","عطیہ دہندہ کی عمر کم از کم 18 سال ہونی چاہیے۔","عطيو ڏيندڙ جي عمر گهٽ ۾ گهٽ 18 سال هجڻ گهرجي."],
["Allow other registered users to contact me directly","دوسرے رجسٹرڈ صارفین کو مجھ سے براہِ راست رابطہ کرنے کی اجازت دیں","ٻين رجسٽر ٿيل استعمال ڪندڙن کي مون سان سڌو رابطو ڪرڻ جي اجازت ڏيو"],
["When enabled, other users can see my phone and WhatsApp buttons in Find Donors and Donor Directory. Your own profile will not show contact buttons to you. You can change this setting later.","فعال ہونے پر دوسرے صارفین کو Find Donors اور Donor Directory میں آپ کے فون اور واٹس ایپ کے بٹن نظر آئیں گے۔ آپ کو اپنے پروفائل پر یہ بٹن نظر نہیں آئیں گے۔ آپ یہ ترتیب بعد میں تبدیل کر سکتے ہیں۔","فعال ٿيڻ تي ٻين استعمال ڪندڙن کي Find Donors ۽ Donor Directory ۾ توهان جا فون ۽ واٽس ايپ بٽڻ نظر ايندا. توهان کي پنهنجي پروفائل تي اهي بٽڻ نظر نه ايندا. توهان هي ترتيب پوءِ تبديل ڪري سگهو ٿا."],
["Select blood group","بلڈ گروپ منتخب کریں","رت جو گروپ چونڊيو"],
["Enter the area where you can travel for a donation.","وہ علاقہ درج کریں جہاں آپ خون عطیہ کرنے کے لیے جا سکتے ہیں۔","اهو علائقو داخل ڪريو جتي توهان رت عطيو ڪرڻ لاءِ وڃي سگهو ٿا."],
["Preferred Hospital (Optional)","پسندیدہ ہسپتال (اختیاری)","پسنديده اسپتال (اختياري)"],
["This is optional and does not replace the hospital selected by a recipient or healthcare professional.","یہ اختیاری ہے اور وصول کنندہ یا طبی ماہر کے منتخب کردہ ہسپتال کی جگہ نہیں لیتا۔","هي اختياري آهي ۽ وصول ڪندڙ يا طبي ماهر جي چونڊيل اسپتال جي جاءِ نٿو وٺي."],
["Have you donated blood before?","کیا آپ نے پہلے خون عطیہ کیا ہے؟","ڇا توهان اڳ ۾ رت عطيو ڪيو آهي؟"],
["No, this is my first time","نہیں، یہ میرا پہلا عطیہ ہے","نه، هي منهنجو پهريون ڀيرو آهي"],
["Yes, I have donated before","جی ہاں، میں پہلے خون عطیہ کر چکا ہوں","ها، مون اڳ ۾ رت عطيو ڪيو آهي"],
["Last Blood Donation Date","آخری خون عطیہ کرنے کی تاریخ","آخري رت عطيو ڪرڻ جي تاريخ"],
["Enter the date of your most recent donation. The date cannot be in the future.","اپنے آخری خون کے عطیے کی تاریخ درج کریں۔ تاریخ مستقبل کی نہیں ہو سکتی۔","پنهنجي آخري رت جي عطئي جي تاريخ داخل ڪريو. تاريخ مستقبل جي نه ٿي سگهي."],
["Health Self-Assessment","صحت کا خود جائزہ","صحت جو ذاتي جائزو"],
["Preliminary Health Questions","ابتدائی صحت سے متعلق سوالات","صحت بابت شروعاتي سوال"],
["Answer all five questions honestly. These answers are for preliminary screening only and do not determine medical eligibility.","پانچوں سوالات کے جواب ایمانداری سے دیں۔ یہ جوابات صرف ابتدائی جانچ کے لیے ہیں اور طبی اہلیت کا حتمی فیصلہ نہیں کرتے۔","پنجن ئي سوالن جا جواب ايمانداري سان ڏيو. اهي جواب صرف شروعاتي جاچ لاءِ آهن ۽ طبي اهليت جو آخري فيصلو نٿا ڪن."],
["Choose an answer","جواب منتخب کریں","جواب چونڊيو"],
["Your health answers are private information. They must not appear on public donor profiles.","آپ کے صحت سے متعلق جوابات نجی معلومات ہیں۔ انہیں عوامی عطیہ دہندہ پروفائلز پر ظاہر نہیں کیا جانا چاہیے۔","توهان جا صحت بابت جواب ذاتي معلومات آهن. اهي عوامي عطيو ڏيندڙ پروفائلن تي ظاهر نه ٿيڻ گهرجن."],
["Health Information Confirmation","صحت کی معلومات کی تصدیق","صحت جي معلومات جي تصديق"],
["Choose an option","ایک آپشن منتخب کریں","هڪ اختيار چونڊيو"],
["I confirm that my answers are accurate.","میں تصدیق کرتا ہوں کہ میرے جوابات درست ہیں۔","مان تصديق ڪريان ٿو ته منهنجا جواب صحيح آهن."],
["A qualified healthcare professional must make the final decision about whether you can donate.","آپ خون عطیہ کر سکتے ہیں یا نہیں، اس کا حتمی فیصلہ مستند طبی ماہر کرے گا۔","توهان رت عطيو ڪري سگهو ٿا يا نه، ان جو آخري فيصلو ماهر طبي عملي ڪندو."],
["Before You Register","اندراج سے پہلے","اندراج کان اڳ"],
["A few important things to remember.","چند اہم باتیں یاد رکھیں۔","ياد رکڻ لاءِ ڪجهه اهم ڳالهيون."],
["Correct Blood Group","درست بلڈ گروپ","صحيح رت جو گروپ"],
["Select your blood group carefully. Medical professionals must confirm blood compatibility before transfusion.","اپنا بلڈ گروپ احتیاط سے منتخب کریں۔ انتقالِ خون سے پہلے طبی ماہرین کو مطابقت کی تصدیق کرنی چاہیے۔","پنهنجو رت جو گروپ احتياط سان چونڊيو. رت چاڙهڻ کان اڳ طبي عملي کي مطابقت جي تصديق ڪرڻ گهرجي."],
["Accurate Location","درست مقام","صحيح هنڌ"],
["Provide your city or area so potential recipients can identify donors in a suitable location.","اپنا شہر یا علاقہ درج کریں تاکہ ممکنہ وصول کنندگان مناسب مقام پر عطیہ دہندگان تلاش کر سکیں۔","پنهنجو شهر يا علائقو ڏيو ته جيئن ممڪن وصول ڪندڙ مناسب هنڌ تي عطيو ڏيندڙ ڳولي سگهن."],
["90-Day Donation Interval","90 دن کا عطیہ وقفہ","90 ڏينهن جو عطئي وارو وقفو"],
["The system uses your last donation date to apply its minimum 90-day interval rule.","سسٹم آخری عطیے کی تاریخ سے کم از کم 90 دن کا وقفہ لاگو کرتا ہے۔","سسٽم آخري عطئي جي تاريخ مان گهٽ ۾ گهٽ 90 ڏينهن جو وقفو لاڳو ڪري ٿو."],
["Private Health Information","نجی صحت کی معلومات","ذاتي صحت جي معلومات"],
["Health answers should be restricted to authorised handling and never shown in public donor search results.","صحت کے جوابات تک رسائی صرف مجاز افراد تک محدود ہونی چاہیے اور انہیں عوامی ڈونر تلاش کے نتائج میں کبھی نہیں دکھانا چاہیے۔","صحت بابت جواب صرف اجازت يافته عملي تائين محدود هجڻ گهرجن ۽ عوامي ڊونر ڳولا جي نتيجن ۾ ڪڏهن به نه ڏيکارڻ گهرجن."],
["Registration does not mean you are medically approved to donate. A qualified healthcare professional must assess your suitability before donation. The system's 90-day rule is an administrative screening rule, not a complete medical eligibility assessment.","رجسٹریشن کا مطلب طبی طور پر خون عطیہ کرنے کی منظوری نہیں ہے۔ عطیہ دینے سے پہلے مستند طبی ماہر آپ کی موزونیت کا جائزہ لے۔ سسٹم کا 90 دن کا اصول انتظامی جانچ ہے، مکمل طبی اہلیت کا متبادل نہیں۔","رجسٽريشن جو مطلب اهو ناهي ته توهان کي طبي طور رت عطيو ڪرڻ جي منظوري ملي وئي آهي. عطئي کان اڳ ماهر طبي عملي کي توهان جي موزونيت جانچڻ گهرجي. سسٽم جو 90 ڏينهن وارو اصول انتظامي جاچ آهي، مڪمل طبي جائزو نه."],
["BLOOD DONOR NETWORK","بلڈ ڈونر نیٹ ورک","رت جي ڊونر نيٽ ورڪ"],
["Blood Donor Directory","بلڈ ڈونر ڈائریکٹری","رت جي ڊونر ڊائريڪٽري"],
["Explore registered blood donors in the network. Review their blood groups, locations, availability and donation eligibility.","نیٹ ورک میں رجسٹرڈ خون کے عطیہ دہندگان دیکھیں۔ ان کے بلڈ گروپ، مقام، دستیابی اور عطیہ دینے کی اہلیت کا جائزہ لیں۔","نيٽ ورڪ ۾ رجسٽر ٿيل رت جا عطيو ڏيندڙ ڏسو. انهن جا رت جا گروپ، هنڌ، دستيابي ۽ عطئي جي اهليت ڏسو."],
["Registered Donors","رجسٹرڈ عطیہ دہندگان","رجسٽر ٿيل عطيو ڏيندڙ"],
["Find donors by name, blood group or location.","نام، بلڈ گروپ یا مقام کے ذریعے عطیہ دہندگان تلاش کریں۔","نالي، رت جي گروپ يا هنڌ ذريعي عطيو ڏيندڙ ڳوليو."],
["Showing","دکھائے جا رہے ہیں","ڏيکاريا پيا وڃن"],
["donor(s)","عطیہ دہندگان","عطيو ڏيندڙ"],
["Your donor profile","آپ کا عطیہ دہندہ پروفائل","توهان جو عطيو ڏيندڙ پروفائل"],
["Your contact is hidden from your own directory card","آپ کا رابطہ نمبر آپ کے اپنے ڈائریکٹری کارڈ پر پوشیدہ ہے","توهان جو رابطو توهان جي پنهنجي ڊائريڪٽري ڪارڊ تي لڪل آهي"],
["Direct contact enabled","براہِ راست رابطہ فعال ہے","سڌو رابطو فعال آهي"],
["Private — donor has not opted in","نجی — عطیہ دہندہ نے اجازت نہیں دی","ذاتي — عطيو ڏيندڙ اجازت نه ڏني آهي"],
["Donation Eligibility","عطیہ دینے کی اہلیت","عطئي جي اهليت"],
["Last Donation","آخری عطیہ","آخري عطيو"],
["Make Not Available","دستیاب نہیں کریں","غير دستياب ڪريو"],
["Make Available","دستیاب کریں","دستياب ڪريو"],
["This is your donor profile. Your contact buttons are hidden from your own account.","یہ آپ کا عطیہ دہندہ پروفائل ہے۔ آپ کے اپنے اکاؤنٹ میں رابطے کے بٹن پوشیدہ ہیں۔","هي توهان جو عطيو ڏيندڙ پروفائل آهي. توهان جي پنهنجي اڪائونٽ ۾ رابطا بٽڻ لڪل آهن."],
["Phone Call","فون کال","فون ڪال"],
["Direct contact is not enabled or this donor is currently unavailable. Open Emergency Request to review compatible requests and manage your matches.","براہِ راست رابطہ فعال نہیں یا یہ عطیہ دہندہ اس وقت دستیاب نہیں۔ موزوں درخواستیں دیکھنے اور میچز منظم کرنے کے لیے Emergency Request کھولیں۔","سڌو رابطو فعال ناهي يا هي عطيو ڏيندڙ هن وقت موجود ناهي. مناسب درخواستون ڏسڻ ۽ ميچ سنڀالڻ لاءِ Emergency Request کوليو."],
["Using your latest active request: # — .","آپ کی تازہ فعال درخواست استعمال ہو رہی ہے: # — ۔","توهان جي تازي فعال درخواست استعمال ٿي رهي آهي: # — ."],
["Request This Donor","اس عطیہ دہندہ سے درخواست کریں","هن عطيو ڏيندڙ کي درخواست موڪليو"],
["No Matching Donors Found","کوئی موزوں عطیہ دہندہ نہیں ملا","ڪو مناسب عطيو ڏيندڙ نه مليو"],
["We couldn't find any donors matching your search. Try another name, blood group or location.","آپ کی تلاش کے مطابق کوئی عطیہ دہندہ نہیں ملا۔ کوئی دوسرا نام، بلڈ گروپ یا مقام آزمائیں۔","توهان جي ڳولا موجب ڪو عطيو ڏيندڙ نه مليو. ٻيو نالو، رت جو گروپ يا هنڌ آزمائي ڏسو."],
["No Donors Registered Yet","ابھی کوئی عطیہ دہندہ رجسٹرڈ نہیں","اڃا ڪو عطيو ڏيندڙ رجسٽر ٿيل ناهي"],
["Registered blood donors will appear here. Donors can register their profiles to become part of the network.","رجسٹرڈ عطیہ دہندگان یہاں نظر آئیں گے۔ نیٹ ورک کا حصہ بننے کے لیے عطیہ دہندگان اپنے پروفائل رجسٹر کر سکتے ہیں۔","رجسٽر ٿيل رت جا عطيو ڏيندڙ هتي نظر ايندا. نيٽ ورڪ جو حصو ٿيڻ لاءِ عطيو ڏيندڙ پنهنجا پروفائل رجسٽر ڪري سگهن ٿا."],
["Emergency Blood Requests","ہنگامی خون کی درخواستیں","هنگامي رت جون درخواستون"],
["Create a blood request, find compatible requests, manage your matches, and track donation and receipt progress in one place.","ایک ہی جگہ پر خون کی درخواست بنائیں، موزوں درخواستیں تلاش کریں، اپنے میچز منظم کریں اور عطیہ و وصولی کی پیش رفت دیکھیں۔","هڪ ئي هنڌ رت جي درخواست ٺاهيو، مناسب درخواستون ڳوليو، پنهنجا ميچ سنڀاليو ۽ عطئي ۽ وصولي جي اڳڀرائي ڏسو."],
["Potential Matches","ممکنہ میچز","ممڪن ميچ"],
["Available Requests","دستیاب درخواستیں","موجود درخواستون"],
["Enter the required details to create a new request.","نئی درخواست بنانے کے لیے مطلوبہ تفصیلات درج کریں۔","نئين درخواست ٺاهڻ لاءِ گهربل تفصيل داخل ڪريو."],
["Required Blood Group","مطلوبہ بلڈ گروپ","گهربل رت جو گروپ"],
["Compatible donor groups:","مطابقت رکھنے والے عطیہ دہندگان کے گروپ:","مطابقت رکندڙ عطيو ڏيندڙن جا گروپ:"],
["Required Units","مطلوبہ یونٹس","گهربل يونٽ"],
["You can request between 1 and 8 units.","آپ 1 سے 8 یونٹس تک درخواست کر سکتے ہیں۔","توهان 1 کان 8 يونٽن تائين درخواست ڪري سگهو ٿا."],
["Contact details are shared with the matched donor only after you confirm the match.","رابطے کی تفصیلات صرف میچ کی تصدیق کے بعد متعلقہ عطیہ دہندہ کے ساتھ شیئر کی جائیں گی۔","رابطي جا تفصيل صرف ميچ جي تصديق کان پوءِ لاڳاپيل عطيو ڏيندڙ سان شيئر ڪيا ويندا."],
["Blood Needed By","خون درکار ہونے کا وقت","رت گهربل هجڻ جو وقت"],
["Select the date and time by which the blood is needed.","وہ تاریخ اور وقت منتخب کریں جس تک خون درکار ہے۔","اها تاريخ ۽ وقت چونڊيو جنهن تائين رت گهربل آهي."],
["Automatic urgency:","خودکار فوری نوعیت:","خودڪار تڪڙ:"],
["If blood is needed within 24 hours, the request will automatically be marked","اگر 24 گھنٹوں کے اندر خون درکار ہو تو درخواست خودکار طور پر نشان زد ہوگی","جيڪڏهن 24 ڪلاڪن اندر رت گهربل هجي ته درخواست پاڻمرادو نشان لڳندي"],
["If more than 24 hours remain, it will be marked","اگر 24 گھنٹوں سے زیادہ وقت باقی ہو تو اسے نشان زد کیا جائے گا","جيڪڏهن 24 ڪلاڪن کان وڌيڪ وقت باقي هجي ته ان کي نشان لڳايو ويندو"],
["You cannot manually select urgency. Pakistan time is used.","آپ فوری نوعیت خود منتخب نہیں کر سکتے۔ پاکستان کا وقت استعمال ہوتا ہے۔","توهان تڪڙ پاڻمرادو چونڊي نٿا سگهو. پاڪستان جو وقت استعمال ٿئي ٿو."],
["Submit Blood Request","خون کی درخواست جمع کریں","رت جي درخواست جمع ڪريو"],
["All active blood requests posted by other users. Accept a request when one of your donor profiles is compatible and eligible.","دوسرے صارفین کی تمام فعال خون کی درخواستیں۔ جب آپ کا کوئی عطیہ دہندہ پروفائل موزوں اور اہل ہو تو درخواست قبول کریں۔","ٻين استعمال ڪندڙن جون سڀ فعال رت جون درخواستون. جڏهن توهان جو ڪو عطيو ڏيندڙ پروفائل مناسب ۽ اهل هجي ته درخواست قبول ڪريو."],
["Blood Required","درکار خون","گهربل رت"],
["Request # · Requested by","درخواست نمبر · درخواست گزار","درخواست نمبر · درخواست ڪندڙ"],
["Total Required","کل مطلوبہ","ڪل گهربل"],
["Units Remaining","باقی یونٹس","باقي يونٽ"],
["Request Created","درخواست بنائی گئی","درخواست ٺاهي وئي"],
["Donation progress","عطیہ کی پیش رفت","عطئي جي اڳڀرائي"],
["Select donor profile","عطیہ دہندہ پروفائل منتخب کریں","عطيو ڏيندڙ پروفائل چونڊيو"],
["Choose a donor profile","عطیہ دہندہ پروفائل منتخب کریں","عطيو ڏيندڙ پروفائل چونڊيو"],
["Units you can donate","آپ کتنے یونٹس عطیہ کر سکتے ہیں","توهان ڪيترا يونٽ عطيو ڪري سگهو ٿا"],
["Accept This Request","یہ درخواست قبول کریں","هي درخواست قبول ڪريو"],
["Accepting this request starts the match immediately. The requester does not need to approve it again. Your private chat becomes available as soon as the match is active. Each donor profile can have only one active match at a time.","اس درخواست کو قبول کرنے سے میچ فوراً شروع ہو جاتا ہے۔ درخواست گزار کی دوبارہ منظوری ضروری نہیں۔ میچ فعال ہوتے ہی نجی چیٹ دستیاب ہو جاتی ہے۔ ہر عطیہ دہندہ پروفائل کا ایک وقت میں صرف ایک فعال میچ ہو سکتا ہے۔","هي درخواست قبول ڪرڻ سان ميچ فوراً شروع ٿئي ٿو. درخواست ڪندڙ جي ٻيهر منظوري جي ضرورت ناهي. ميچ فعال ٿيندي ئي ذاتي چيٽ موجود ٿيندي. هر عطيو ڏيندڙ پروفائل جو هڪ وقت ۾ صرف هڪ فعال ميچ ٿي سگهي ٿو."],
["No compatible requests available","کوئی موزوں درخواست دستیاب نہیں","ڪا مناسب درخواست موجود ناهي"],
["There are currently no unexpired blood requests matching your available eligible donor profiles.","اس وقت آپ کے دستیاب اور اہل عطیہ دہندہ پروفائلز سے مطابقت رکھنے والی کوئی غیر میعاد ختم شدہ درخواست موجود نہیں۔","هن وقت توهان جي موجود ۽ اهل عطيو ڏيندڙ پروفائلن سان ملندڙ ڪا غير ختم ٿيل درخواست موجود ناهي."],
["Track the requests you have created.","اپنی بنائی ہوئی درخواستوں کی پیش رفت دیکھیں۔","پنهنجين ٺاهيل درخواستن جي اڳڀرائي ڏسو."],
["Cancel My Request","میری درخواست منسوخ کریں","منهنجي درخواست رد ڪريو"],
["You have not created any requests","آپ نے ابھی کوئی درخواست نہیں بنائی","توهان اڃا ڪا درخواست نه ٺاهي آهي"],
["Your blood requests will appear here after you submit them.","آپ کی خون کی درخواستیں جمع ہونے کے بعد یہاں نظر آئیں گی۔","توهان جون رت جون درخواستون جمع ٿيڻ کان پوءِ هتي نظر اينديون."],
["Compatible donors, accepted matches, private chat, and the complete donation coordination process are managed here.","مطابقت رکھنے والے عطیہ دہندگان، قبول شدہ میچز، نجی چیٹ اور عطیہ کی مکمل رابطہ کاری یہاں منظم ہوتی ہے۔","مطابقت رکندڙ عطيو ڏيندڙ، قبول ٿيل ميچ، ذاتي چيٽ ۽ عطئي جو مڪمل انتظام هتي ڪيو ويندو آهي."],
["Potential Donor Found","ممکنہ عطیہ دہندہ مل گیا","ممڪن عطيو ڏيندڙ مليو"],
["A Compatible Request Is Waiting","ایک موزوں درخواست منتظر ہے","هڪ مناسب درخواست انتظار ۾ آهي"],
["Potential Donor Group","ممکنہ عطیہ دہندہ کا بلڈ گروپ","ممڪن عطيو ڏيندڙ جو رت جو گروپ"],
["Your Donor Group","آپ کا عطیہ دہندہ بلڈ گروپ","توهان جو عطيو ڏيندڙ رت جو گروپ"],
["Units Required","مطلوبہ یونٹس","گهربل يونٽ"],
["This donor is compatible and eligible for your request. Accept once to activate the match. The donor will see the same active match and can coordinate with you in this chat.","یہ عطیہ دہندہ آپ کی درخواست کے لیے موزوں اور اہل ہے۔ میچ فعال کرنے کے لیے ایک بار قبول کریں۔ عطیہ دہندہ بھی یہی فعال میچ دیکھ سکے گا اور اس چیٹ میں آپ سے رابطہ کر سکے گا۔","هي عطيو ڏيندڙ توهان جي درخواست لاءِ مناسب ۽ اهل آهي. ميچ فعال ڪرڻ لاءِ هڪ ڀيرو قبول ڪريو. عطيو ڏيندڙ به ساڳيو فعال ميچ ڏسي سگهندو ۽ هن چيٽ ۾ توهان سان رابطو ڪري سگهندو."],
["Accept This Donor &amp; Start Match","اس عطیہ دہندہ کو قبول کریں اور میچ شروع کریں","هن عطيو ڏيندڙ کي قبول ڪري ميچ شروع ڪريو"],
["Your donor profile matches this request by blood group and city. Accept once to start the match immediately. Private chat and contact actions become available after acceptance.","آپ کا عطیہ دہندہ پروفائل بلڈ گروپ اور شہر کے لحاظ سے اس درخواست سے مطابقت رکھتا ہے۔ میچ فوراً شروع کرنے کے لیے ایک بار قبول کریں۔ قبولیت کے بعد نجی چیٹ اور رابطے کے اختیارات دستیاب ہوں گے۔","توهان جو عطيو ڏيندڙ پروفائل رت جي گروپ ۽ شهر موجب هن درخواست سان ملي ٿو. ميچ فوراً شروع ڪرڻ لاءِ هڪ ڀيرو قبول ڪريو. قبوليت کان پوءِ ذاتي چيٽ ۽ رابطي جا اختيار موجود ٿيندا."],
["Accept & Start Match","قبول کریں اور میچ شروع کریں","قبول ڪريو ۽ ميچ شروع ڪريو"],
["Your donor request has been sent. The match and private chat will start when the donor accepts.","آپ کی عطیہ دہندہ درخواست بھیج دی گئی ہے۔ عطیہ دہندہ کے قبول کرنے پر میچ اور نجی چیٹ شروع ہو جائے گی۔","توهان جي عطيو ڏيندڙ درخواست موڪلي وئي آهي. عطيو ڏيندڙ جي قبول ڪرڻ تي ميچ ۽ ذاتي چيٽ شروع ٿيندي."],
["This requester has invited you to donate. Accept once to start the match and private chat.","اس درخواست گزار نے آپ کو خون عطیہ کرنے کی دعوت دی ہے۔ میچ اور نجی چیٹ شروع کرنے کے لیے ایک بار قبول کریں۔","هن درخواست ڪندڙ توهان کي رت عطيو ڪرڻ جي دعوت ڏني آهي. ميچ ۽ ذاتي چيٽ شروع ڪرڻ لاءِ هڪ ڀيرو قبول ڪريو."],
["Accept Donor Request","عطیہ دہندہ کی درخواست قبول کریں","عطيو ڏيندڙ جي درخواست قبول ڪريو"],
["A donor has accepted your request. Confirm the match to allow the matched parties to access their contact actions.","ایک عطیہ دہندہ نے آپ کی درخواست قبول کر لی ہے۔ متعلقہ افراد کو رابطے کے اختیارات دینے کے لیے میچ کی تصدیق کریں۔","هڪ عطيو ڏيندڙ توهان جي درخواست قبول ڪئي آهي. لاڳاپيل ماڻهن کي رابطي جا اختيار ڏيڻ لاءِ ميچ جي تصديق ڪريو."],
["Confirm Match","میچ کی تصدیق کریں","ميچ جي تصديق ڪريو"],
["Reject Match","میچ مسترد کریں","ميچ رد ڪريو"],
["Your acceptance is waiting for the requester to confirm. You can cancel it before confirmation.","آپ کی قبولیت درخواست گزار کی تصدیق کی منتظر ہے۔ تصدیق سے پہلے آپ اسے منسوخ کر سکتے ہیں۔","توهان جي قبوليت درخواست ڪندڙ جي تصديق جي انتظار ۾ آهي. تصديق کان اڳ توهان ان کي رد ڪري سگهو ٿا."],
["Cancel My Acceptance","میری قبولیت منسوخ کریں","منهنجي قبوليت رد ڪريو"],
["Match active.","میچ فعال ہے۔","ميچ فعال آهي."],
["Contact actions are available according to the donor's contact-sharing setting.","رابطے کے اختیارات عطیہ دہندہ کی رابطہ شیئرنگ ترتیب کے مطابق دستیاب ہیں۔","رابطي جا اختيار عطيو ڏيندڙ جي رابطي شيئر ڪرڻ واري ترتيب موجب موجود آهن."],
["Contact information is not available.","رابطے کی معلومات دستیاب نہیں۔","رابطي جي معلومات موجود ناهي."],
["Contact information remains private until the requester confirms this match.","درخواست گزار کی جانب سے میچ کی تصدیق تک رابطے کی معلومات نجی رہیں گی۔","درخواست ڪندڙ جي ميچ جي تصديق تائين رابطي جي معلومات ذاتي رهندي."],
["Private Match Chat","میچ کی نجی چیٹ","ميچ جي ذاتي چيٽ"],
["Only you and the matched donor requester can read this conversation. Discuss the request here while confirmation is pending. Phone and WhatsApp details remain private until confirmation.","یہ گفتگو صرف آپ اور میچ میں شامل عطیہ دہندہ اور درخواست گزار پڑھ سکتے ہیں۔ تصدیق زیرِ انتظار ہونے کے دوران یہاں درخواست پر بات کریں۔ فون اور واٹس ایپ کی تفصیلات تصدیق تک نجی رہیں گی۔","هي گفتگو صرف توهان ۽ ميچ ۾ شامل عطيو ڏيندڙ ۽ درخواست ڪندڙ پڙهي سگهن ٿا. تصديق جي انتظار دوران هتي درخواست بابت ڳالهه ٻولهه ڪريو. فون ۽ واٽس ايپ جا تفصيل تصديق تائين ذاتي رهندا."],
["No messages yet. Start a private conversation with your match.","ابھی کوئی پیغام نہیں۔ اپنے میچ کے ساتھ نجی گفتگو شروع کریں۔","اڃا ڪو پيغام ناهي. پنهنجي ميچ سان ذاتي ڳالهه ٻولهه شروع ڪريو."],
["After receiving the blood, record the actual units and donation date here. A confirmed copy will automatically appear in the donor's profile history.","خون وصول کرنے کے بعد اصل یونٹس اور عطیے کی تاریخ یہاں درج کریں۔ تصدیق شدہ نقل خودکار طور پر عطیہ دہندہ کے پروفائل کی تاریخ میں محفوظ ہو جائے گی۔","رت وصول ڪرڻ کان پوءِ اصل يونٽ ۽ عطئي جي تاريخ هتي داخل ڪريو. تصديق ٿيل ڪاپي پاڻمرادو عطيو ڏيندڙ جي پروفائل جي تاريخ ۾ محفوظ ٿيندي."],
["Units Received","موصول ہونے والے یونٹس","وصول ٿيل يونٽ"],
["Donation Date","عطیہ کرنے کی تاریخ","عطئي جي تاريخ"],
["Record Received Donation","موصول شدہ عطیہ درج کریں","وصول ٿيل عطيو درج ڪريو"],
["Donation reported. The requester must confirm receipt before this match is completed.","عطیہ رپورٹ ہو گیا۔ میچ مکمل ہونے سے پہلے درخواست گزار کو وصولی کی تصدیق کرنا ہوگی۔","عطئي جي رپورٽ ٿي وئي. ميچ مڪمل ٿيڻ کان اڳ درخواست ڪندڙ کي وصولي جي تصديق ڪرڻي پوندي."],
["This match has been completed. The donation and receipt process is finished.","یہ میچ مکمل ہو چکا ہے۔ عطیہ اور وصولی کا عمل ختم ہو گیا ہے۔","هي ميچ مڪمل ٿي چڪو آهي. عطئي ۽ وصولي جو عمل پورو ٿيو آهي."],
["No matches yet","ابھی کوئی میچ نہیں","اڃا ڪو ميچ ناهي"],
["No eligible donor or open blood request currently matches your blood group and city. New potential matches will appear here when compatible availability is found.","اس وقت کوئی اہل عطیہ دہندہ یا کھلی خون کی درخواست آپ کے بلڈ گروپ اور شہر سے مطابقت نہیں رکھتی۔ موزوں دستیابی ملنے پر نئے ممکنہ میچ یہاں نظر آئیں گے۔","هن وقت ڪو اهل عطيو ڏيندڙ يا کليل رت جي درخواست توهان جي رت جي گروپ ۽ شهر سان نٿي ملي. مناسب دستيابي ملڻ تي نوان ممڪن ميچ هتي نظر ايندا."],
["Helping connect blood donors with people in need.","خون کے عطیہ دہندگان کو ضرورت مند افراد سے ملانے میں مدد۔","رت جي عطيو ڏيندڙن کي ضرورت مند ماڻهن سان ڳنڍڻ ۾ مدد."],
["Stay updated about your blood donation and emergency request activity.","اپنے خون کے عطیے اور ہنگامی درخواستوں کی سرگرمی سے باخبر رہیں۔","پنهنجي رت جي عطئي ۽ هنگامي درخواستن جي سرگرمين بابت باخبر رهو."],
["Activity Centre","سرگرمیوں کا مرکز","سرگرمين جو مرڪز"],
["No donation records are available yet.","ابھی عطیے کا کوئی ریکارڈ دستیاب نہیں۔","اڃا عطئي جو ڪو رڪارڊ موجود ناهي."],
["No Notifications Yet","ابھی کوئی اطلاع نہیں","اڃا ڪا اطلاع ناهي"],
["Request updates, donor acceptances, match confirmations, private chat messages, donation reports, receipt confirmations, and other account activity will appear here.","درخواستوں کی تازہ کاری، عطیہ دہندگان کی قبولیت، میچ کی تصدیق، نجی چیٹ پیغامات، عطیے کی رپورٹس، وصولی کی تصدیق اور اکاؤنٹ کی دیگر سرگرمیاں یہاں ظاہر ہوں گی۔","درخواستن جون تازه ڪاريون، عطيو ڏيندڙن جون قبوليتون، ميچ جي تصديق، ذاتي چيٽ پيغام، عطئي جون رپورٽون، وصولي جي تصديق ۽ اڪائونٽ جون ٻيون سرگرميون هتي ظاهر ٿينديون."],
["Manage your account and view your personal activity.","اپنا اکاؤنٹ منظم کریں اور اپنی ذاتی سرگرمیاں دیکھیں۔","پنهنجو اڪائونٽ سنڀاليو ۽ پنهنجون ذاتي سرگرميون ڏسو."],
["Registered account","رجسٹرڈ اکاؤنٹ","رجسٽر ٿيل اڪائونٽ"],
["Completed Donations","مکمل عطیات","مڪمل ٿيل عطيا"],
["View donation history","عطیے کی تاریخ دیکھیں","عطئي جي تاريخ ڏسو"],
["Total Blood Requests","خون کی کل درخواستیں","رت جون ڪل درخواستون"],
["View request history","درخواستوں کی تاریخ دیکھیں","درخواستن جي تاريخ ڏسو"],
["My Activity","میری سرگرمیاں","منهنجون سرگرميون"],
["My Donor Profiles","میرے عطیہ دہندگان کے پروفائلز","منهنجا عطيو ڏيندڙ پروفائل"],
["You have not registered as a blood donor yet.","آپ نے ابھی بطور خون عطیہ دہندہ رجسٹریشن نہیں کی۔","توهان اڃا رت جي عطيو ڏيندڙ طور رجسٽريشن نه ڪئي آهي."],
["You have no donation records yet.","آپ کا ابھی عطیے کا کوئی ریکارڈ نہیں۔","توهان وٽ اڃا عطئي جو ڪو رڪارڊ ناهي."],
["You have not created any blood requests yet.","آپ نے ابھی خون کی کوئی درخواست نہیں بنائی۔","توهان اڃا رت جي ڪا درخواست نه ٺاهي آهي."],
["Find registered donors using the patient's blood group and location. The platform identifies compatible blood groups and displays donor availability information.","مریض کے بلڈ گروپ اور مقام کے ذریعے رجسٹرڈ عطیہ دہندگان تلاش کریں۔ پلیٹ فارم موزوں بلڈ گروپس کی نشاندہی کرتا ہے اور عطیہ دہندگان کی دستیابی دکھاتا ہے۔","مريض جي رت جي گروپ ۽ هنڌ ذريعي رجسٽر ٿيل عطيو ڏيندڙ ڳوليو. پليٽ فارم مناسب رت جي گروپن جي سڃاڻپ ڪري ٿو ۽ عطيو ڏيندڙن جي دستيابي ڏيکاري ٿو."],
["Search registered donors using the patient's blood group and location. The platform identifies compatible blood groups and displays donor availability information.","مریض کے بلڈ گروپ اور مقام کے ذریعے رجسٹرڈ عطیہ دہندگان تلاش کریں۔ پلیٹ فارم موزوں بلڈ گروپس کی نشاندہی کرتا ہے اور عطیہ دہندگان کی دستیابی دکھاتا ہے۔","مريض جي رت جي گروپ ۽ هنڌ ذريعي رجسٽر ٿيل عطيو ڏيندڙ ڳوليو. پليٽ فارم مناسب رت جي گروپن جي سڃاڻپ ڪري ٿو ۽ عطيو ڏيندڙن جي دستيابي ڏيکاري ٿو."],
["Select the patient's required blood group and enter a city or area. Compatible donor groups will be identified automatically.","مریض کا مطلوبہ بلڈ گروپ منتخب کریں اور شہر یا علاقہ درج کریں۔ موزوں عطیہ دہندگان کے گروپس خودکار طور پر شناخت کیے جائیں گے۔","مريض جو گهربل رت جو گروپ چونڊيو ۽ شهر يا علائقو داخل ڪريو. مناسب عطيو ڏيندڙن جا گروپ پاڻمرادو سڃاتا ويندا."],
["Patient's Blood Group","مریض کا بلڈ گروپ","مريض جو رت جو گروپ"],
["Compatible Donor Blood Groups","مطابقت رکھنے والے عطیہ دہندگان کے بلڈ گروپس","مطابقت رکندڙ عطيو ڏيندڙن جا رت جا گروپ"],
["These groups are based on the platform's red blood cell compatibility rules. A blood bank or qualified healthcare professional must confirm compatibility before transfusion.","یہ گروپس پلیٹ فارم کے سرخ خون کے خلیات کی مطابقت کے اصولوں پر مبنی ہیں۔ انتقالِ خون سے پہلے بلڈ بینک یا مستند طبی ماہر کو مطابقت کی تصدیق کرنی چاہیے۔","اهي گروپ پليٽ فارم جي ڳاڙهن رت جي خلين جي مطابقت جي اصولن تي ٻڌل آهن. رت چاڙهڻ کان اڳ بلڊ بئنڪ يا ماهر طبي عملي کي مطابقت جي تصديق ڪرڻ گهرجي."],
["Matching Donors","مطابقت رکھنے والے عطیہ دہندگان","مطابقت رکندڙ عطيو ڏيندڙ"],
["No matching donor was found for this blood group and location. Try another nearby area. For urgent needs, contact a hospital or blood bank as well.","اس بلڈ گروپ اور مقام کے لیے کوئی موزوں عطیہ دہندہ نہیں ملا۔ قریبی دوسرا علاقہ آزمائیں۔ فوری ضرورت کے لیے ہسپتال یا بلڈ بینک سے بھی رابطہ کریں۔","هن رت جي گروپ ۽ هنڌ لاءِ ڪو مناسب عطيو ڏيندڙ نه مليو. ويجهو ٻيو علائقو آزمائي ڏسو. تڪڙي ضرورت لاءِ اسپتال يا بلڊ بئنڪ سان به رابطو ڪريو."],
["Direct call and WhatsApp details are shown only when a donor has opted in. Otherwise, contact becomes available to both parties after a match is confirmed. Private in-app chat is available from the My Matches section in Emergency Request after a donor accepts a request.","براہِ راست کال اور واٹس ایپ کی تفصیلات صرف اسی وقت دکھائی جاتی ہیں جب عطیہ دہندہ اجازت دے۔ بصورتِ دیگر میچ کی تصدیق کے بعد دونوں فریق رابطہ کر سکتے ہیں۔ عطیہ دہندہ کی قبولیت کے بعد Emergency Request کے My Matches حصے میں نجی چیٹ دستیاب ہوتی ہے۔","سڌي ڪال ۽ واٽس ايپ جا تفصيل صرف تڏهن ڏيکاريا ويندا آهن جڏهن عطيو ڏيندڙ اجازت ڏئي. ٻي صورت ۾ ميچ جي تصديق کان پوءِ ٻئي ڌريون رابطو ڪري سگهن ٿيون. عطيو ڏيندڙ جي قبوليت کان پوءِ Emergency Request جي My Matches حصي ۾ ذاتي چيٽ موجود هوندي."],
["Donors shown here are marked according to their registered availability and system eligibility. This is not final medical clearance. A qualified healthcare professional or blood bank must assess donor suitability and perform required compatibility testing before any transfusion.","یہاں دکھائے گئے عطیہ دہندگان کی دستیابی اور سسٹم کی اہلیت ان کی رجسٹریشن کے مطابق ہے۔ یہ حتمی طبی منظوری نہیں۔ انتقالِ خون سے پہلے مستند طبی ماہر یا بلڈ بینک کو عطیہ دہندہ کی موزونیت اور مطابقت کے ضروری ٹیسٹ کرنے چاہئیں۔","هتي ڏيکاريل عطيو ڏيندڙن جي دستيابي ۽ سسٽم جي اهليت سندن رجسٽريشن موجب آهي. اها آخري طبي منظوري ناهي. رت چاڙهڻ کان اڳ ماهر طبي عملي يا بلڊ بئنڪ کي عطيو ڏيندڙ جي موزونيت ۽ ضروري مطابقت جا ٽيسٽ ڪرڻ گهرجن."],
["Important Medical Information","اہم طبی معلومات","اهم طبي معلومات"],
["Record a completed donation and update your donation history.","مکمل شدہ عطیے کا اندراج کریں اور اپنی عطیے کی تاریخ اپ ڈیٹ کریں۔","مڪمل ٿيل عطيو درج ڪريو ۽ پنهنجي عطئي جي تاريخ اپڊيٽ ڪريو."],
["Enter the details of the donation that has already taken place. Do not report a donation before it has occurred.","اس عطیے کی تفصیلات درج کریں جو پہلے ہی ہو چکا ہے۔ عطیہ ہونے سے پہلے اس کی رپورٹ نہ کریں۔","ان عطئي جا تفصيل داخل ڪريو جيڪو اڳ ۾ ٿي چڪو آهي. عطيو ٿيڻ کان اڳ ان جي رپورٽ نه ڏيو."],
["Your report may be linked to a blood request. The requester must confirm receipt before the donated units count toward the request's fulfilled quantity.","آپ کی رپورٹ خون کی درخواست سے منسلک ہو سکتی ہے۔ عطیہ کیے گئے یونٹس درخواست کی تکمیل میں شمار ہونے سے پہلے درخواست گزار کو وصولی کی تصدیق کرنا ہوگی۔","توهان جي رپورٽ رت جي درخواست سان ڳنڍجي سگهي ٿي. عطيو ڪيل يونٽ درخواست جي مڪمل مقدار ۾ ڳڻجڻ کان اڳ درخواست ڪندڙ کي وصولي جي تصديق ڪرڻي پوندي."],
["Units Donated","عطیہ کیے گئے یونٹس","عطيو ڪيل يونٽ"],
["Enter the actual number of units donated.","عطیہ کیے گئے یونٹس کی اصل تعداد درج کریں۔","عطيو ڪيل يونٽن جو اصل تعداد داخل ڪريو."],
["Related Blood Request","متعلقہ خون کی درخواست","لاڳاپيل رت جي درخواست"],
["Not linked to a specific request","کسی مخصوص درخواست سے منسلک نہیں","ڪنهن مخصوص درخواست سان ڳنڍيل ناهي"],
["Select the request you donated for, if applicable.","اگر قابلِ اطلاق ہو تو وہ درخواست منتخب کریں جس کے لیے آپ نے خون عطیہ کیا۔","جيڪڏهن لاڳو ٿئي ته اها درخواست چونڊيو جنهن لاءِ توهان رت عطيو ڪيو."],
["Hospital / Blood Bank","ہسپتال / بلڈ بینک","اسپتال / بلڊ بئنڪ"],
["City / Location","شہر / مقام","شهر / هنڌ"],
["Additional Notes (Optional)","اضافی نوٹس (اختیاری)","اضافي نوٽ (اختياري)"],
["Submit Donation Report","عطیے کی رپورٹ جمع کریں","عطئي جي رپورٽ جمع ڪريو"],
["Report Blood Donation","خون کے عطیے کی رپورٹ","رت جي عطئي جي رپورٽ"],
["Match status:","میچ کی حیثیت:","ميچ جي حيثيت:"],
["Donor:","عطیہ دہندہ:","عطيو ڏيندڙ:"],
["Requester:","درخواست گزار:","درخواست ڪندڙ:"],
["Contact details","رابطے کی تفصیلات","رابطي جا تفصيل"],
["Contact details become available after the requester confirms this match.","درخواست گزار کی جانب سے میچ کی تصدیق کے بعد رابطے کی تفصیلات دستیاب ہوں گی۔","درخواست ڪندڙ جي ميچ جي تصديق کان پوءِ رابطي جا تفصيل موجود ٿيندا."],
["Donation date","عطیے کی تاریخ","عطئي جي تاريخ"],
["Units donated","عطیہ کیے گئے یونٹس","عطيو ڪيل يونٽ"],
["Report donation","عطیے کی رپورٹ","عطئي جي رپورٽ"],
["Pending","زیرِ التوا","انتظار ۾"],
["Fulfilled","مکمل","مڪمل"],
["Cancelled","منسوخ","رد ٿيل"],
["Expired","میعاد ختم","مدو پورو"],
["Confirmed","تصدیق شدہ","تصديق ٿيل"],
["Reported","رپورٹ شدہ","رپورٽ ٿيل"],
["Accepted","قبول شدہ","قبول ٿيل"],
["Rejected","مسترد","رد ٿيل"],
["Completed","مکمل","مڪمل"],
["Active","فعال","فعال"],
["Invited","دعوت دی گئی","دعوت ڏنل"],
["No","نہیں","نه"],
["Yes","ہاں","ها"],
["Search Donors","عطیہ دہندگان تلاش کریں","عطيو ڏيندڙ ڳوليو"],
["found","مل گئے","مليا"],
["years","سال","سال"],
["Age:","عمر:","عمر:"],
["Location:","مقام:","هنڌ:"],
["Last Donation:","آخری عطیہ:","آخري عطيو:"],
["units","یونٹس","يونٽ"],
["unit(s)","یونٹ","يونٽ"],
["Request History","درخواستوں کی تاریخ","درخواستن جي تاريخ"],
["Active Requests","فعال درخواستیں","فعال درخواستون"],
["Completed Requests","مکمل درخواستیں","مڪمل درخواستون"],
["Donation History","عطیے کی تاریخ","عطئي جي تاريخ"],
["No messages yet.","ابھی کوئی پیغام نہیں۔","اڃا ڪو پيغام ناهي."],
["Open Private Chat","نجی چیٹ کھولیں","ذاتي چيٽ کوليو"],
["View Potential Matches","ممکنہ میچز دیکھیں","ممڪن ميچ ڏسو"],
["Open Potential Matches","ممکنہ میچز کھولیں","ممڪن ميچ کوليو"],
["View Available Requests","دستیاب درخواستیں دیکھیں","موجود درخواستون ڏسو"],
["View My Requests","میری درخواستیں دیکھیں","منهنجون درخواستون ڏسو"],
["View Donor Profile","عطیہ دہندہ کا پروفائل دیکھیں","عطيو ڏيندڙ جو پروفائل ڏسو"],
["Open Dashboard","ڈیش بورڈ کھولیں","ڊيش بورڊ کوليو"],
["Mark as read","پڑھا ہوا نشان زد کریں","پڙهيل طور نشان لڳايو"],
["Read","پڑھی ہوئی","پڙهيل"],
["NEW","نیا","نئون"],
["unread · total","غیر پڑھی ہوئی · کل","اڻپڙهيل · ڪل"],
["Search Compatible Donors","موزوں عطیہ دہندگان تلاش کریں","مناسب عطيو ڏيندڙ ڳوليو"],
["Clear Filters","فلٹر صاف کریں","فلٽر صاف ڪريو"],
["Enter city or area","شہر یا علاقہ درج کریں","شهر يا علائقو داخل ڪريو"],
["Find compatible blood donors","مطابقت رکھنے والے خون کے عطیہ دہندگان تلاش کریں","مطابقت رکندڙ رت جا عطيو ڏيندڙ ڳوليو"],
["Request for Blood","خون کی درخواست کریں","رت لاءِ درخواست ڪريو"],
["Create a blood request first. After submitting it, return here to request this donor.","پہلے خون کی درخواست بنائیں۔ اسے جمع کرنے کے بعد یہاں واپس آ کر اس عطیہ دہندہ سے درخواست کریں۔","پهرين رت جي درخواست ٺاهيو. اها جمع ڪرڻ کان پوءِ هتي واپس اچي هن عطيو ڏيندڙ کي درخواست موڪليو."],
["Create an active blood request first, then return to the donor directory to request this donor.","پہلے ایک فعال خون کی درخواست بنائیں، پھر اس عطیہ دہندہ سے درخواست کرنے کے لیے ڈونر ڈائریکٹری میں واپس آئیں۔","پهرين فعال رت جي درخواست ٺاهيو، پوءِ هن عطيو ڏيندڙ کي درخواست ڪرڻ لاءِ ڊونر ڊائريڪٽري ڏانهن واپس اچو."]
["Connecting donors. Supporting lives.","عطیہ دہندگان کو جوڑنا، زندگیوں کا سہارا بننا۔","عطيو ڏيندڙن کي ڳنڍڻ، زندگين جو سهارو بڻجڻ."],
["When every second counts, every drop matters.","جب ہر لمحہ قیمتی ہو، خون کا ہر قطرہ اہم ہوتا ہے۔","جڏهن هر لمحو اهم هجي، رت جو هر قطرو اهم آهي."],
["Explore compatible blood groups, create emergency requests and coordinate donation progress.","موزوں بلڈ گروپس دیکھیں، ہنگامی درخواستیں بنائیں اور عطیے کی پیش رفت میں رابطہ کاری کریں۔","مناسب رت جا گروپ ڏسو، هنگامي درخواستون ٺاهيو ۽ عطئي جي اڳڀرائي ۾ سهڪار ڪريو."],
["A small act can make a big difference.","ایک چھوٹا سا عمل بڑا فرق پیدا کر سکتا ہے۔","هڪ ننڍڙو عمل وڏو فرق آڻي سگهي ٿو."],
["One connected network","ایک مربوط نیٹ ورک","هڪ ڳنڍيل نيٽ ورڪ"],
["Supporting donor discovery, emergency requests and donation coordination.","عطیہ دہندگان کی تلاش، ہنگامی درخواستوں اور عطیے کی رابطہ کاری میں مدد۔","عطيو ڏيندڙن جي ڳولا، هنگامي درخواستن ۽ عطئي جي سهڪار ۾ مدد."],
["Bringing blood donors and people in need together","خون کے عطیہ دہندگان اور ضرورت مند افراد کو ایک جگہ لانا","رت جا عطيو ڏيندڙ ۽ ضرورت مند ماڻهو گڏ آڻڻ"],
["Our Mission","ہمارا مقصد","اسان جو مقصد"],
["Our Vision","ہمارا وژن","اسان جو خواب"],
["A simple and organized process","ایک آسان اور منظم طریقۂ کار","هڪ سادو ۽ منظم طريقو"],
["Create Your Account","اپنا اکاؤنٹ بنائیں","پنهنجو اڪائونٽ ٺاهيو"],
["Explore or Request Blood","خون تلاش کریں یا درخواست دیں","رت ڳوليو يا درخواست ڏيو"],
["Match, Donate and Confirm","میچ، عطیہ اور تصدیق","ميچ، عطيو ۽ تصديق"],
["How the complete matching process works","میچنگ کا مکمل طریقۂ کار","ميچنگ جو مڪمل طريقو"],
["A requester creates a blood request and specifies the required blood group and units.","درخواست گزار خون کی درخواست بناتا ہے اور مطلوبہ بلڈ گروپ اور یونٹس بتاتا ہے۔","درخواست ڪندڙ رت جي درخواست ٺاهي گهربل رت جو گروپ ۽ يونٽ ڄاڻائي ٿو."],
["The platform identifies potentially compatible, available and eligible donors.","پلیٹ فارم ممکنہ طور پر موزوں، دستیاب اور اہل عطیہ دہندگان کی نشاندہی کرتا ہے۔","پليٽ فارم ممڪن طور مناسب، موجود ۽ اهل عطيو ڏيندڙن جي سڃاڻپ ڪري ٿو."],
["The requester reviews and confirms or rejects the proposed match.","درخواست گزار مجوزہ میچ کا جائزہ لے کر اس کی تصدیق یا اسے مسترد کرتا ہے۔","درخواست ڪندڙ تجويز ڪيل ميچ جو جائزو وٺي ان جي تصديق يا رد ڪري ٿو."],
["Once confirmed, the matched parties can contact each other using Call and WhatsApp actions.","تصدیق کے بعد دونوں فریق کال اور واٹس ایپ کے ذریعے ایک دوسرے سے رابطہ کر سکتے ہیں۔","تصديق کان پوءِ ٻئي ڌريون ڪال ۽ واٽس ايپ ذريعي هڪ ٻئي سان رابطو ڪري سگهن ٿيون."],
["The donor reports the donation and the requester confirms the actual units received.","عطیہ دہندہ عطیے کی رپورٹ دیتا ہے اور درخواست گزار موصول ہونے والے اصل یونٹس کی تصدیق کرتا ہے۔","عطيو ڏيندڙ عطئي جي رپورٽ ڏئي ٿو ۽ درخواست ڪندڙ وصول ٿيل اصل يونٽن جي تصديق ڪري ٿو."],
["Confirmed received units reduce the remaining requirement.","موصول شدہ تصدیق شدہ یونٹس باقی ضرورت کو کم کرتے ہیں۔","تصديق ٿيل وصول ٿيل يونٽ باقي ضرورت گهٽائين ٿا."],
["Select a blood group to view compatible donor groups and relevant blood requests.","موزوں عطیہ دہندگان کے گروپس اور متعلقہ خون کی درخواستیں دیکھنے کے لیے بلڈ گروپ منتخب کریں۔","مناسب عطيو ڏيندڙن جا گروپ ۽ لاڳاپيل رت جون درخواستون ڏسڻ لاءِ رت جو گروپ چونڊيو."],
["Private contact details and CNIC information are not displayed.","ذاتی رابطے کی تفصیلات اور CNIC کی معلومات ظاہر نہیں کی جاتیں۔","ذاتي رابطي جا تفصيل ۽ CNIC جي معلومات ظاهر نه ڪئي ويندي آهي."],
["Names and blood groups are shown to help visitors explore the community; personal contact details remain private.","کمیونٹی کو دیکھنے کے لیے نام اور بلڈ گروپس دکھائے جاتے ہیں؛ ذاتی رابطے کی تفصیلات نجی رہتی ہیں۔","ڪميونٽي ڏسڻ لاءِ نالا ۽ رت جا گروپ ڏيکاريا وڃن ٿا؛ ذاتي رابطي جا تفصيل نجي رهن ٿا."],
["No donor profiles have been registered yet.","ابھی تک کسی عطیہ دہندہ کا پروفائل رجسٹر نہیں ہوا۔","اڃا تائين ڪنهن عطيو ڏيندڙ جو پروفائل رجسٽر ناهي ٿيو."],
["Current requests that still need blood donations.","موجودہ درخواستیں جنہیں ابھی خون کے عطیات درکار ہیں۔","موجوده درخواستون جن کي اڃا رت جي عطين جي ضرورت آهي."],
["There are no active blood requests at the moment.","اس وقت خون کی کوئی فعال درخواست موجود نہیں۔","هن وقت رت جي ڪا به فعال درخواست موجود ناهي."],
["This platform does not replace medical advice, clinical screening or blood-bank procedures.","یہ پلیٹ فارم طبی مشورے، طبی جانچ یا بلڈ بینک کے طریقۂ کار کا متبادل نہیں ہے۔","هي پليٽ فارم طبي صلاح، ڪلينڪل جاچ يا بلڊ بئنڪ جي طريقيڪار جو متبادل ناهي."],
["About the Blood Donor Network","بلڈ ڈونر نیٹ ورک کے بارے میں","رت جي عطيو ڏيندڙ نيٽ ورڪ بابت"],
["The platform supports donor registration, blood request matching, secure communication after match confirmation, and donation receipt tracking.","یہ پلیٹ فارم عطیہ دہندگان کے اندراج، خون کی درخواستوں کی میچنگ، میچ کی تصدیق کے بعد محفوظ رابطے اور عطیے کی وصولی کی نگرانی میں مدد دیتا ہے۔","هي پليٽ فارم عطيو ڏيندڙن جي رجسٽريشن، رت جي درخواستن جي ميچنگ، ميچ جي تصديق کان پوءِ محفوظ رابطي ۽ عطئي جي وصولي جي نگراني ۾ مدد ڪري ٿو."],
["Contact details are kept private until a match is confirmed by the requester.","درخواست گزار کی جانب سے میچ کی تصدیق تک رابطے کی تفصیلات نجی رکھی جاتی ہیں۔","درخواست ڪندڙ طرفان ميچ جي تصديق تائين رابطي جا تفصيل نجي رکيا وڃن ٿا."],
["Eligible donors can review compatible requests and send an acceptance.","اہل عطیہ دہندگان موزوں درخواستوں کا جائزہ لے کر قبولیت بھیج سکتے ہیں۔","اهل عطيو ڏيندڙ مناسب درخواستن جو جائزو وٺي قبوليت موڪلي سگهن ٿا."],
["Secure Account Access","محفوظ اکاؤنٹ تک رسائی","اڪائونٽ تائين محفوظ رسائي"],
["Every drop can make a difference.","خون کا ہر قطرہ فرق پیدا کر سکتا ہے۔","رت جو هر قطرو فرق آڻي سگهي ٿو."],
["Connect with blood donors, discover donation opportunities, and help people find support when every moment matters.","خون کے عطیہ دہندگان سے رابطہ کریں، عطیے کے مواقع تلاش کریں اور اہم لمحات میں لوگوں کو مدد حاصل کرنے میں معاون بنیں۔","رت جي عطيو ڏيندڙن سان رابطو ڪريو، عطئي جا موقعا ڳوليو ۽ اهم لمحن ۾ ماڻهن کي مدد حاصل ڪرڻ ۾ سهڪار ڪريو."],
["Find compatible donors","موزوں عطیہ دہندگان تلاش کریں","مناسب عطيو ڏيندڙ ڳوليو"],
["Search for donors according to blood group and location.","بلڈ گروپ اور مقام کے مطابق عطیہ دہندگان تلاش کریں۔","رت جي گروپ ۽ هنڌ موجب عطيو ڏيندڙ ڳوليو."],
["Support emergency requests","ہنگامی درخواستوں میں مدد کریں","هنگامي درخواستن ۾ مدد ڪريو"],
["Access blood requests and help connect patients with donors.","خون کی درخواستیں دیکھیں اور مریضوں کو عطیہ دہندگان سے جوڑنے میں مدد کریں۔","رت جون درخواستون ڏسو ۽ مريضن کي عطيو ڏيندڙن سان ڳنڍڻ ۾ مدد ڪريو."],
["Make a meaningful difference","بامعنی فرق پیدا کریں","بامعنيٰ فرق آڻيو"],
["Manage your donor profile and stay connected with the network.","اپنا عطیہ دہندہ پروفائل منظم کریں اور نیٹ ورک سے منسلک رہیں۔","پنهنجو عطيو ڏيندڙ پروفائل سنڀاليو ۽ نيٽ ورڪ سان ڳنڍيل رهو."],
["Sign in to your account","اپنے اکاؤنٹ میں سائن اِن کریں","پنهنجي اڪائونٽ ۾ سائن اِن ڪريو"],
["Enter your registered email or phone number to continue.","جاری رکھنے کے لیے اپنا رجسٹرڈ ای میل یا فون نمبر درج کریں۔","اڳتي وڌڻ لاءِ پنهنجو رجسٽر ٿيل اي ميل يا فون نمبر داخل ڪريو."],
["Email or phone number","ای میل یا فون نمبر","اي ميل يا فون نمبر"],
["BECOME PART OF THE NETWORK","نیٹ ورک کا حصہ بنیں","نيٽ ورڪ جو حصو بڻجو"],
["Join the network. Help save lives.","نیٹ ورک میں شامل ہوں۔ زندگیاں بچانے میں مدد کریں۔","نيٽ ورڪ ۾ شامل ٿيو. زندگيون بچائڻ ۾ مدد ڪريو."],
["Connect with donors","عطیہ دہندگان سے رابطہ کریں","عطيو ڏيندڙن سان رابطو ڪريو"],
["Request emergency blood","ہنگامی خون کی درخواست دیں","هنگامي رت جي درخواست ڏيو"],
["Create blood requests and connect with potential donors.","خون کی درخواستیں بنائیں اور ممکنہ عطیہ دہندگان سے رابطہ کریں۔","رت جون درخواستون ٺاهيو ۽ ممڪن عطيو ڏيندڙن سان رابطو ڪريو."],
["Enter your details below to join the Blood Donor Network.","بلڈ ڈونر نیٹ ورک میں شامل ہونے کے لیے نیچے اپنی تفصیلات درج کریں۔","رت جي عطيو ڏيندڙ نيٽ ورڪ ۾ شامل ٿيڻ لاءِ هيٺ پنهنجا تفصيل داخل ڪريو."],
["Full Name","پورا نام","پورو نالو"],
["CNIC Number","شناختی کارڈ نمبر","شناختي ڪارڊ نمبر"],
["Enter your 13-digit CNIC.","اپنا 13 ہندسوں پر مشتمل CNIC درج کریں۔","پنهنجو 13 انگن وارو CNIC داخل ڪريو."],
["It is used for registration and must never appear on public profiles.","یہ صرف رجسٹریشن کے لیے استعمال ہوتا ہے اور عوامی پروفائلز پر ہرگز ظاہر نہیں ہونا چاہیے۔","اهو صرف رجسٽريشن لاءِ استعمال ٿئي ٿو ۽ عوامي پروفائلن تي ڪڏهن به ظاهر نه ٿيڻ گهرجي."],
["Email Address","ای میل ایڈریس","اي ميل پتو"],
["Provide at least one login identifier: email address or phone number.","لاگ اِن کے لیے کم از کم ایک شناخت فراہم کریں: ای میل ایڈریس یا فون نمبر۔","لاگ اِن لاءِ گهٽ ۾ گهٽ هڪ سڃاڻپ ڏيو: اي ميل پتو يا فون نمبر."],
["Your password must contain at least 8 characters.","آپ کے پاس ورڈ میں کم از کم 8 حروف ہونے چاہئیں۔","توهان جي پاسورڊ ۾ گهٽ ۾ گهٽ 8 اکر هجڻ گهرجن."],
["Donor Registration","عطیہ دہندہ کا اندراج","عطيو ڏيندڙ جي رجسٽريشن"],
["Contact Number","رابطے کا نمبر","رابطي جو نمبر"],
["Allow other registered users to contact me directly","دوسرے رجسٹرڈ صارفین کو مجھ سے براہِ راست رابطہ کرنے کی اجازت دیں","ٻين رجسٽر ٿيل استعمال ڪندڙن کي مون سان سڌو رابطو ڪرڻ جي اجازت ڏيو"],
["City / Area","شہر / علاقہ","شهر / علائقو"],
["Enter the area where you can travel for a donation.","وہ علاقہ درج کریں جہاں آپ خون عطیہ کرنے کے لیے جا سکتے ہیں۔","اهو علائقو داخل ڪريو جتي توهان رت عطيو ڪرڻ لاءِ وڃي سگهو ٿا."],
["Preferred Hospital (Optional)","پسندیدہ ہسپتال (اختیاری)","پسنديده اسپتال (اختياري)"],
["Have you donated blood before?","کیا آپ نے پہلے خون عطیہ کیا ہے؟","ڇا توهان اڳ ۾ رت عطيو ڪيو آهي؟"],
["No, this is my first time","نہیں، یہ میرا پہلا عطیہ ہے","نه، هي منهنجو پهريون عطيو آهي"],
["Yes, I have donated before","جی ہاں، میں پہلے خون عطیہ کر چکا ہوں","ها، مون اڳ ۾ رت عطيو ڪيو آهي"],
["Last Blood Donation Date","آخری خون عطیہ کرنے کی تاریخ","آخري رت عطيو ڪرڻ جي تاريخ"],
["Health Self-Assessment","صحت کا خود جائزہ","صحت جو ذاتي جائزو"],
["Preliminary Health Questions","ابتدائی صحت سے متعلق سوالات","صحت بابت شروعاتي سوال"],
["Choose an answer","جواب منتخب کریں","جواب چونڊيو"],
["Health Information Confirmation","صحت کی معلومات کی تصدیق","صحت جي معلومات جي تصديق"],
["Before You Register","رجسٹریشن سے پہلے","رجسٽريشن کان اڳ"],
["A few important things to remember.","چند اہم باتیں یاد رکھیں۔","ڪجهه اهم ڳالهيون ياد رکو."],
["Correct Blood Group","درست بلڈ گروپ","صحيح رت جو گروپ"],
["Accurate Location","درست مقام","صحيح هنڌ"],
["90-Day Donation Interval","90 دن کا عطیہ وقفہ","90 ڏينهن جو عطئي وارو وقفو"],
["Private Health Information","نجی صحت کی معلومات","نجي صحت جي معلومات"],
["Find donors by name, blood group or location.","نام، بلڈ گروپ یا مقام کے مطابق عطیہ دہندگان تلاش کریں۔","نالي، رت جي گروپ يا هنڌ موجب عطيو ڏيندڙ ڳوليو."],
["Patient's Blood Group","مریض کا بلڈ گروپ","مريض جو رت جو گروپ"],
["Showing donor(s)","عطیہ دہندگان دکھائے جا رہے ہیں","عطيو ڏيندڙ ڏيکاريا پيا وڃن"],
["Your donor profile","آپ کا عطیہ دہندہ پروفائل","توهان جو عطيو ڏيندڙ پروفائل"],
["Direct contact enabled","براہِ راست رابطہ فعال ہے","سڌو رابطو فعال آهي"],
["Private — donor has not opted in","نجی — عطیہ دہندہ نے اجازت نہیں دی","نجي — عطيو ڏيندڙ اجازت نه ڏني آهي"],
["Donation Eligibility","عطیہ دینے کی اہلیت","عطيو ڏيڻ جي اهليت"],
["Not Eligible","اہل نہیں","اهل ناهي"],
["Last Donation","آخری عطیہ","آخري عطيو"],
["Make Not Available","غیر دستیاب کریں","غير موجود ڪريو"],
["Make Available","دستیاب کریں","موجود ڪريو"],
["No Matching Donors Found","کوئی موزوں عطیہ دہندہ نہیں ملا","ڪو مناسب عطيو ڏيندڙ نه مليو"],
["We couldn't find any donors matching your search. Try another name, blood group or location.","آپ کی تلاش کے مطابق کوئی عطیہ دہندہ نہیں ملا۔ کوئی دوسرا نام، بلڈ گروپ یا مقام آزمائیں۔","توهان جي ڳولا موجب ڪو عطيو ڏيندڙ نه مليو. ٻيو نالو، رت جو گروپ يا هنڌ آزمائي ڏسو."],
["No Donors Registered Yet","ابھی تک کوئی عطیہ دہندہ رجسٹر نہیں ہوا","اڃا تائين ڪو عطيو ڏيندڙ رجسٽر ناهي ٿيو"],
["Create a blood request, find compatible requests, manage your matches, and track donation and receipt progress in one place.","ایک ہی جگہ خون کی درخواست بنائیں، موزوں درخواستیں تلاش کریں، اپنے میچز منظم کریں اور عطیے و وصولی کی پیش رفت دیکھیں۔","هڪ ئي هنڌ رت جي درخواست ٺاهيو، مناسب درخواستون ڳوليو، پنهنجا ميچ سنڀاليو ۽ عطئي توڙي وصولي جي اڳڀرائي ڏسو."],
["Create Request","درخواست بنائیں","درخواست ٺاهيو"],
["My Requests","میری درخواستیں","منهنجون درخواستون"],
["Potential Matches","ممکنہ میچز","ممڪن ميچ"],
["Available Requests","دستیاب درخواستیں","موجود درخواستون"],
["Enter the required details to create a new request.","نئی درخواست بنانے کے لیے مطلوبہ تفصیلات درج کریں۔","نئين درخواست ٺاهڻ لاءِ گهربل تفصيل داخل ڪريو."],
["Required Units","مطلوبہ یونٹس","گهربل يونٽ"],
["You can request between 1 and 8 units.","آپ 1 سے 8 یونٹس تک درخواست دے سکتے ہیں۔","توهان 1 کان 8 يونٽن تائين درخواست ڏئي سگهو ٿا."],
["Hospital Name","ہسپتال کا نام","اسپتال جو نالو"],
["Select the date and time by which the blood is needed.","وہ تاریخ اور وقت منتخب کریں جس تک خون درکار ہے۔","اها تاريخ ۽ وقت چونڊيو جنهن تائين رت گهربل آهي."],
["Automatic urgency:","فوری نوعیت خودکار طور پر طے ہوگی:","تڪڙ پاڻمرادو طئي ٿيندي:"],
["If blood is needed within 24 hours, the request will automatically be marked Emergency.","اگر 24 گھنٹوں کے اندر خون درکار ہو تو درخواست خودکار طور پر ہنگامی قرار دی جائے گی۔","جيڪڏهن 24 ڪلاڪن اندر رت گهربل هجي ته درخواست پاڻمرادو هنگامي قرار ڏني ويندي."],
["If more than 24 hours remain, it will be marked Normal.","اگر 24 گھنٹوں سے زیادہ وقت باقی ہو تو اسے عام قرار دیا جائے گا۔","جيڪڏهن 24 ڪلاڪن کان وڌيڪ وقت باقي هجي ته ان کي عام قرار ڏنو ويندو."],
["You cannot manually select urgency.","آپ فوری نوعیت خود منتخب نہیں کر سکتے۔","توهان تڪڙ پاڻمرادو چونڊي نٿا سگهو."],
["Pakistan time is used.","پاکستان کا مقامی وقت استعمال ہوتا ہے۔","پاڪستان جو مقامي وقت استعمال ٿئي ٿو."],
["Submit Blood Request","خون کی درخواست جمع کریں","رت جي درخواست جمع ڪريو"],
["All active blood requests posted by other users.","دوسرے صارفین کی تمام فعال خون کی درخواستیں۔","ٻين استعمال ڪندڙن جون سڀ فعال رت جون درخواستون."],
["Accept a request when one of your donor profiles is compatible and eligible.","جب آپ کا کوئی عطیہ دہندہ پروفائل موزوں اور اہل ہو تو درخواست قبول کریں۔","جڏهن توهان جو ڪو عطيو ڏيندڙ پروفائل مناسب ۽ اهل هجي ته درخواست قبول ڪريو."],
["Request Created","درخواست بنائی گئی","درخواست ٺاهي وئي"],
["Blood Needed By","خون درکار ہونے کی آخری تاریخ","رت گهربل ٿيڻ جي آخري تاريخ"],
["Donation progress","عطیے کی پیش رفت","عطئي جي اڳڀرائي"],
["Select donor profile","عطیہ دہندہ پروفائل منتخب کریں","عطيو ڏيندڙ پروفائل چونڊيو"],
["Units you can donate","آپ کتنے یونٹس عطیہ کر سکتے ہیں","توهان ڪيترا يونٽ عطيو ڪري سگهو ٿا"],
["Accept This Request","یہ درخواست قبول کریں","هي درخواست قبول ڪريو"],
["Accepting this request starts the match immediately.","یہ درخواست قبول کرنے سے میچ فوراً شروع ہو جاتا ہے۔","هي درخواست قبول ڪرڻ سان ميچ فوراً شروع ٿئي ٿو."],
["The requester does not need to approve it again.","درخواست گزار کو دوبارہ منظوری دینے کی ضرورت نہیں۔","درخواست ڪندڙ کي ٻيهر منظوري ڏيڻ جي ضرورت ناهي."],
["Your private chat becomes available as soon as the match is active.","میچ فعال ہوتے ہی نجی چیٹ دستیاب ہو جاتی ہے۔","ميچ فعال ٿيندي ئي ذاتي چيٽ موجود ٿي وڃي ٿي."],
["Each donor profile can have only one active match at a time.","ہر عطیہ دہندہ پروفائل کا ایک وقت میں صرف ایک فعال میچ ہو سکتا ہے۔","هر عطيو ڏيندڙ پروفائل جو هڪ وقت ۾ صرف هڪ فعال ميچ ٿي سگهي ٿو."],
["No compatible requests available","کوئی موزوں درخواست دستیاب نہیں","ڪا مناسب درخواست موجود ناهي"],
["Track the requests you have created.","اپنی بنائی ہوئی درخواستوں کی نگرانی کریں۔","توهان جي ٺاهيل درخواستن جي نگراني ڪريو."],
["Cancel My Request","میری درخواست منسوخ کریں","منهنجي درخواست رد ڪريو"],
["Your blood requests will appear here after you submit them.","آپ کی جمع کرائی گئی خون کی درخواستیں یہاں دکھائی دیں گی۔","توهان جون جمع ڪرايل رت جون درخواستون هتي ظاهر ٿينديون."],
["Compatible donors, accepted matches, private chat, and the complete donation coordination process are managed here.","موزوں عطیہ دہندگان، قبول شدہ میچز، نجی چیٹ اور عطیے کی مکمل رابطہ کاری یہاں منظم کی جاتی ہے۔","مناسب عطيو ڏيندڙ، قبول ٿيل ميچ، ذاتي چيٽ ۽ عطئي جو مڪمل سهڪار هتي سنڀاليو وڃي ٿو."],
["Potential Donor Found","ممکنہ عطیہ دہندہ مل گیا","ممڪن عطيو ڏيندڙ مليو"],
["A Compatible Request Is Waiting","ایک موزوں درخواست منتظر ہے","هڪ مناسب درخواست انتظار ۾ آهي"],
["Potential Donor Group","ممکنہ عطیہ دہندہ کا بلڈ گروپ","ممڪن عطيو ڏيندڙ جو رت جو گروپ"],
["Your Donor Group","آپ کا بلڈ گروپ","توهان جو رت جو گروپ"],
["This donor is compatible and eligible for your request.","یہ عطیہ دہندہ آپ کی درخواست کے لیے موزوں اور اہل ہے۔","هي عطيو ڏيندڙ توهان جي درخواست لاءِ مناسب ۽ اهل آهي."],
["Accept once to activate the match.","میچ فعال کرنے کے لیے صرف ایک بار قبول کریں۔","ميچ فعال ڪرڻ لاءِ صرف هڪ ڀيرو قبول ڪريو."],
["Accept This Donor & Start Match","اس عطیہ دہندہ کو قبول کریں اور میچ شروع کریں","هن عطيو ڏيندڙ کي قبول ڪري ميچ شروع ڪريو"],
["Your donor profile matches this request by blood group and city.","آپ کا عطیہ دہندہ پروفائل بلڈ گروپ اور شہر کے لحاظ سے اس درخواست سے مطابقت رکھتا ہے۔","توهان جو عطيو ڏيندڙ پروفائل رت جي گروپ ۽ شهر موجب هن درخواست سان ملي ٿو."],
["Private chat and contact actions become available after acceptance.","قبولیت کے بعد نجی چیٹ اور رابطے کے اختیارات دستیاب ہو جاتے ہیں۔","قبوليت کان پوءِ ذاتي چيٽ ۽ رابطي جا اختيار موجود ٿين ٿا."],
["Accept & Start Match","قبول کریں اور میچ شروع کریں","قبول ڪريو ۽ ميچ شروع ڪريو"],
["A donor has accepted your request.","ایک عطیہ دہندہ نے آپ کی درخواست قبول کر لی ہے۔","هڪ عطيو ڏيندڙ توهان جي درخواست قبول ڪئي آهي."],
["Confirm the match to allow the matched parties to access their contact actions.","دونوں فریقوں کو رابطے کے اختیارات دینے کے لیے میچ کی تصدیق کریں۔","ٻنهي ڌرين کي رابطي جا اختيار ڏيڻ لاءِ ميچ جي تصديق ڪريو."],
["Your acceptance is waiting for the requester to confirm.","آپ کی قبولیت درخواست گزار کی تصدیق کی منتظر ہے۔","توهان جي قبوليت درخواست ڪندڙ جي تصديق جي انتظار ۾ آهي."],
["You can cancel it before confirmation.","تصدیق سے پہلے آپ اسے منسوخ کر سکتے ہیں۔","تصديق کان اڳ توهان ان کي رد ڪري سگهو ٿا."],
["Cancel My Acceptance","میری قبولیت منسوخ کریں","منهنجي قبوليت رد ڪريو"],
["Call Donor","عطیہ دہندہ کو کال کریں","عطيو ڏيندڙ کي ڪال ڪريو"],
["WhatsApp Donor","عطیہ دہندہ کو واٹس ایپ کریں","عطيو ڏيندڙ کي واٽس ايپ ڪريو"],
["Call Requester","درخواست گزار کو کال کریں","درخواست ڪندڙ کي ڪال ڪريو"],
["WhatsApp Requester","درخواست گزار کو واٹس ایپ کریں","درخواست ڪندڙ کي واٽس ايپ ڪريو"],
["Contact information is not available.","رابطے کی معلومات دستیاب نہیں۔","رابطي جي معلومات موجود ناهي."],
["Private Match Chat","نجی میچ چیٹ","ذاتي ميچ چيٽ"],
["Only you and the matched donor requester can read this conversation.","یہ گفتگو صرف آپ اور میچ ہونے والے عطیہ دہندہ یا درخواست گزار کو نظر آتی ہے۔","هي گفتگو صرف توهان ۽ ميچ ٿيل عطيو ڏيندڙ يا درخواست ڪندڙ پڙهي سگهن ٿا."],
["Discuss the request here while confirmation is pending.","تصدیق زیرِ التوا ہونے کے دوران یہاں درخواست پر بات کریں۔","تصديق انتظار ۾ هئڻ دوران هتي درخواست بابت ڳالهايو."],
["Phone and WhatsApp details remain private until confirmation.","تصدیق تک فون اور واٹس ایپ کی تفصیلات نجی رہتی ہیں۔","تصديق تائين فون ۽ واٽس ايپ جا تفصيل نجي رهن ٿا."],
["Start a private conversation with your match.","اپنے میچ کے ساتھ نجی گفتگو شروع کریں۔","پنهنجي ميچ سان ذاتي ڳالهه ٻولهه شروع ڪريو."],
["After receiving the blood, record the actual units and donation date here.","خون موصول ہونے کے بعد یہاں اصل یونٹس اور عطیے کی تاریخ درج کریں۔","رت ملڻ کان پوءِ هتي اصل يونٽ ۽ عطئي جي تاريخ درج ڪريو."],
["A confirmed copy will automatically appear in the donor's profile history.","تصدیق شدہ نقل خودکار طور پر عطیہ دہندہ کے پروفائل کی تاریخ میں ظاہر ہو جائے گی۔","تصديق ٿيل ڪاپي پاڻمرادو عطيو ڏيندڙ جي پروفائل جي تاريخ ۾ ظاهر ٿيندي."],
["Record Received Donation","موصول شدہ عطیہ درج کریں","وصول ٿيل عطيو درج ڪريو"],
["Donation reported. The requester must confirm receipt before this match is completed.","عطیے کی رپورٹ درج ہو گئی۔ میچ مکمل ہونے سے پہلے درخواست گزار کو وصولی کی تصدیق کرنا ہوگی۔","عطئي جي رپورٽ داخل ٿي وئي. ميچ مڪمل ٿيڻ کان اڳ درخواست ڪندڙ کي وصولي جي تصديق ڪرڻي پوندي."],
["This match has been completed.","یہ میچ مکمل ہو چکا ہے۔","هي ميچ مڪمل ٿي چڪو آهي."],
["The donation and receipt process is finished.","عطیے اور وصولی کا عمل مکمل ہو گیا ہے۔","عطئي ۽ وصولي جو عمل مڪمل ٿي ويو آهي."],
["No matches yet","ابھی کوئی میچ نہیں","اڃا ڪو ميچ ناهي"],
["No eligible donor or open blood request currently matches your blood group and city.","اس وقت آپ کے بلڈ گروپ اور شہر سے مطابقت رکھنے والا کوئی اہل عطیہ دہندہ یا کھلی خون کی درخواست موجود نہیں۔","هن وقت توهان جي رت جي گروپ ۽ شهر سان ملندڙ ڪو اهل عطيو ڏيندڙ يا کليل رت جي درخواست موجود ناهي."],
["New potential matches will appear here when compatible availability is found.","موزوں دستیابی ملنے پر نئے ممکنہ میچ یہاں ظاہر ہوں گے۔","مناسب دستيابي ملڻ تي نوان ممڪن ميچ هتي ظاهر ٿيندا."],
["Available compatible donors","دستیاب موزوں عطیہ دہندگان","موجود مناسب عطيو ڏيندڙ"],
["No eligible compatible donors are currently listed.","اس وقت کوئی اہل اور موزوں عطیہ دہندہ فہرست میں موجود نہیں۔","هن وقت ڪو اهل ۽ مناسب عطيو ڏيندڙ فهرست ۾ موجود ناهي."],
["Open blood requests","کھلی خون کی درخواستیں","کليل رت جون درخواستون"],
["No open requests for this blood group are currently listed.","اس بلڈ گروپ کے لیے اس وقت کوئی کھلی درخواست فہرست میں موجود نہیں۔","هن رت جي گروپ لاءِ هن وقت ڪا کليل درخواست فهرست ۾ موجود ناهي."],
["Contact details are not shown publicly.","رابطے کی تفصیلات عوامی طور پر نہیں دکھائی جاتیں۔","رابطي جا تفصيل عوامي طور ظاهر نٿا ڪيا وڃن."],
["Create an account to participate.","حصہ لینے کے لیے اکاؤنٹ بنائیں۔","حصو وٺڻ لاءِ اڪائونٽ ٺاهيو."],
["No donation records are available yet.","ابھی عطیے کا کوئی ریکارڈ دستیاب نہیں۔","اڃا عطئي جو ڪو رڪارڊ موجود ناهي."],
["Record a completed donation and update your donation history.","مکمل شدہ عطیے کا اندراج کریں اور اپنی عطیے کی تاریخ اپ ڈیٹ کریں۔","مڪمل ٿيل عطيو درج ڪريو ۽ پنهنجي عطئي جي تاريخ اپڊيٽ ڪريو."],
["Registered blood donor","رجسٹرڈ خون کا عطیہ دہندہ","رجسٽر ٿيل رت جو عطيو ڏيندڙ"],
["Donation Details","عطیے کی تفصیلات","عطئي جا تفصيل"],
["Enter the details of the donation that has already taken place. Do not report a donation before it has occurred.","اس عطیے کی تفصیلات درج کریں جو پہلے ہی ہو چکا ہے۔ عطیہ ہونے سے پہلے اس کی رپورٹ نہ کریں۔","ان عطئي جا تفصيل داخل ڪريو جيڪو اڳ ۾ ٿي چڪو آهي. عطيو ٿيڻ کان اڳ ان جي رپورٽ نه ڏيو."],
["Your report may be linked to a blood request. The requester must confirm receipt before the donated units count toward the request's fulfilled quantity.","آپ کی رپورٹ خون کی درخواست سے منسلک ہو سکتی ہے۔ عطیہ کیے گئے یونٹس درخواست کی تکمیل میں شمار ہونے سے پہلے درخواست گزار کو وصولی کی تصدیق کرنا ہوگی۔","توهان جي رپورٽ رت جي درخواست سان ڳنڍجي سگهي ٿي. عطيو ڪيل يونٽ درخواست جي مڪمل مقدار ۾ ڳڻجڻ کان اڳ درخواست ڪندڙ کي وصولي جي تصديق ڪرڻي پوندي."],
["Related Blood Request","متعلقہ خون کی درخواست","لاڳاپيل رت جي درخواست"],
["Not linked to a specific request","کسی مخصوص درخواست سے منسلک نہیں","ڪنهن مخصوص درخواست سان ڳنڍيل ناهي"],
["Select the request you donated for, if applicable.","اگر قابلِ اطلاق ہو تو وہ درخواست منتخب کریں جس کے لیے آپ نے خون عطیہ کیا۔","جيڪڏهن لاڳو ٿئي ته اها درخواست چونڊيو جنهن لاءِ توهان رت عطيو ڪيو."],
["Additional Notes (Optional)","اضافی نوٹس (اختیاری)","اضافي نوٽ (اختياري)"],
["Submit Donation Report","عطیے کی رپورٹ جمع کریں","عطئي جي رپورٽ جمع ڪريو"],
["Back to Donor Directory","عطیہ دہندگان کی فہرست پر واپس جائیں","عطيو ڏيندڙن جي فهرست ڏانهن واپس وڃو"],
["Activity Centre","سرگرمیوں کا مرکز","سرگرمين جو مرڪز"],
["Stay updated about your blood donation and emergency request activity.","اپنی خون کے عطیے اور ہنگامی درخواستوں کی سرگرمیوں سے باخبر رہیں۔","پنهنجي رت جي عطئي ۽ هنگامي درخواستن جي سرگرمين کان باخبر رهو."],
["Request updates, donor acceptances, match confirmations, private chat messages, donation reports, receipt confirmations, and other account activity will appear here.","درخواستوں کی تازہ معلومات، عطیہ دہندگان کی قبولیت، میچ کی تصدیق، نجی چیٹ کے پیغامات، عطیے کی رپورٹس، وصولی کی تصدیق اور اکاؤنٹ کی دیگر سرگرمیاں یہاں دکھائی دیں گی۔","درخواستن جون تازه ڪاريون، عطيو ڏيندڙن جون قبوليتون، ميچ جي تصديق، ذاتي چيٽ جا پيغام، عطئي جون رپورٽون، وصولي جي تصديق ۽ اڪائونٽ جون ٻيون سرگرميون هتي ظاهر ٿينديون."],
["Manage your account and view your personal activity.","اپنا اکاؤنٹ منظم کریں اور اپنی ذاتی سرگرمیاں دیکھیں۔","پنهنجو اڪائونٽ سنڀاليو ۽ پنهنجون ذاتي سرگرميون ڏسو."],
["Registered account","رجسٹرڈ اکاؤنٹ","رجسٽر ٿيل اڪائونٽ"],
["Not provided","فراہم نہیں کیا گیا","فراهم ناهي ڪيو ويو"],
["My Activity","میری سرگرمیاں","منهنجون سرگرميون"],
["Completed Donations","مکمل شدہ عطیات","مڪمل ٿيل عطيا"],
["View donation history","عطیے کی تاریخ دیکھیں","عطئي جي تاريخ ڏسو"],
["Total Blood Requests","خون کی کل درخواستیں","رت جون ڪل درخواستون"],
["View request history","درخواستوں کی تاریخ دیکھیں","درخواستن جي تاريخ ڏسو"],
["Health Screening","صحت کی جانچ","صحت جي جاچ"],
["Edit This Donor Profile","اس عطیہ دہندہ پروفائل میں ترمیم کریں","هن عطيو ڏيندڙ پروفائل ۾ ترميم ڪريو"],
["You have not registered as a blood donor yet.","آپ نے ابھی تک بطور خون عطیہ دہندہ رجسٹریشن نہیں کی۔","توهان اڃا تائين رت جي عطيو ڏيندڙ طور رجسٽريشن ناهي ڪئي."],
["Create your donor profile","اپنا عطیہ دہندہ پروفائل بنائیں","پنهنجو عطيو ڏيندڙ پروفائل ٺاهيو"],
["You have no donation records yet.","آپ کے عطیے کا ابھی کوئی ریکارڈ موجود نہیں۔","توهان وٽ اڃا عطئي جو ڪو رڪارڊ ناهي."],
["You have not created any blood requests yet.","آپ نے ابھی تک خون کی کوئی درخواست نہیں بنائی۔","توهان اڃا تائين رت جي ڪا درخواست ناهي ٺاهي."],
["Main navigation","مرکزی نیویگیشن","مکيه نيويگيشن"],
["Open navigation menu","نیویگیشن مینو کھولیں","نيويگيشن مينيو کوليو"],
["Close navigation menu","نیویگیشن مینو بند کریں","نيويگيشن مينيو بند ڪريو"],
["New emergency blood request:","خون کی نئی ہنگامی درخواست:","رت جي نئين هنگامي درخواست:"],
["New normal blood request:","خون کی نئی عام درخواست:","رت جي نئين عام درخواست:"],
["location:","مقام:","هنڌ:"],
["Blood needed by:","خون درکار ہونے کی آخری تاریخ:","رت گهربل ٿيڻ جي آخري تاريخ:"],
["Pakistan time","پاکستان کا مقامی وقت","پاڪستان جو مقامي وقت"],
["A compatible donor has arrived:","ایک موزوں عطیہ دہندہ دستیاب ہو گیا ہے:","هڪ مناسب عطيو ڏيندڙ مليو آهي:"],
["Open Potential Matches to review.","جائزہ لینے کے لیے ممکنہ میچز کھولیں۔","جائزو وٺڻ لاءِ ممڪن ميچ کوليو."],
["Donation reminder for blood request","خون کی درخواست کے لیے عطیے کی یاد دہانی","رت جي درخواست لاءِ عطئي جي ياد ڏيارڻ"],
["Please coordinate your donation with the requester.","براہِ کرم درخواست گزار کے ساتھ عطیے کا انتظام کریں۔","مهرباني ڪري درخواست ڪندڙ سان عطئي جو بندوبست ڪريو."],
["Your blood request has been fully fulfilled.","آپ کی خون کی درخواست مکمل طور پر پوری ہو گئی ہے۔","توهان جي رت جي درخواست مڪمل ٿي وئي آهي."],
["Match Request Found:","میچ کے لیے درخواست مل گئی:","ميچ لاءِ درخواست ملي آهي:"],
["Deadline:","آخری وقت:","آخري وقت:"],
["You have a new private message in your blood request match.","آپ کے خون کی درخواست کے میچ میں آپ کے لیے ایک نیا نجی پیغام ہے۔","توهان جي رت جي درخواست واري ميچ ۾ توهان لاءِ نئون ذاتي پيغام آهي."],
["The requester rejected your acceptance.","درخواست گزار نے آپ کی قبولیت مسترد کر دی ہے۔","درخواست ڪندڙ توهان جي قبوليت رد ڪري ڇڏي آهي."],
["The requester confirmed your match.","درخواست گزار نے آپ کے میچ کی تصدیق کر دی ہے۔","درخواست ڪندڙ توهان جي ميچ جي تصديق ڪري ڇڏي آهي."],
["You can now coordinate the donation.","اب آپ عطیے کے انتظام کے لیے رابطہ کر سکتے ہیں۔","هاڻي توهان عطئي جي بندوبست لاءِ رابطو ڪري سگهو ٿا."],
["You confirmed a donor match for your request.","آپ نے اپنی درخواست کے لیے عطیہ دہندہ کے میچ کی تصدیق کر دی ہے۔","توهان پنهنجي درخواست لاءِ عطيو ڏيندڙ جي ميچ جي تصديق ڪئي آهي."],
["A donor cancelled their pending acceptance.","ایک عطیہ دہندہ نے اپنی زیرِ التوا قبولیت منسوخ کر دی ہے۔","هڪ عطيو ڏيندڙ پنهنجي انتظار واري قبوليت رد ڪري ڇڏي آهي."],
["The request is no longer open or its deadline passed.","درخواست اب کھلی نہیں ہے یا اس کی آخری تاریخ گزر چکی ہے۔","درخواست هاڻي کليل ناهي يا ان جي آخري تاريخ گذري وئي آهي."],
["The requester recorded receipt of","درخواست گزار نے وصولی درج کی ہے","درخواست ڪندڙ وصولي درج ڪئي آهي"],
["You recorded receipt of","آپ نے وصولی درج کی ہے","توهان وصولي درج ڪئي آهي"],
["The requester confirmed receipt of","درخواست گزار نے وصولی کی تصدیق کر دی ہے","درخواست ڪندڙ وصولي جي تصديق ڪري ڇڏي آهي"],
["Please log in to continue.","جاری رکھنے کے لیے لاگ اِن کریں۔","اڳتي وڌڻ لاءِ لاگ اِن ڪريو."],
["Please complete all required donor details.","براہِ کرم عطیہ دہندہ کی تمام لازمی تفصیلات مکمل کریں۔","مهرباني ڪري عطيو ڏيندڙ جا سڀ ضروري تفصيل مڪمل ڪريو."],
["Please enter a valid age.","براہِ کرم درست عمر درج کریں۔","مهرباني ڪري صحيح عمر داخل ڪريو."],
["Donors must be between 18 and 100 years old.","عطیہ دہندگان کی عمر 18 سے 100 سال کے درمیان ہونی چاہیے۔","عطيو ڏيندڙن جي عمر 18 کان 100 سالن جي وچ ۾ هجڻ گهرجي."],
["Please enter a valid contact number.","براہِ کرم درست رابطہ نمبر درج کریں۔","مهرباني ڪري صحيح رابطي جو نمبر داخل ڪريو."],
["Please select your donation history.","براہِ کرم اپنے عطیے کی سابقہ معلومات منتخب کریں۔","مهرباني ڪري پنهنجي عطئي جي اڳوڻي معلومات چونڊيو."],
["Please enter your last donation date.","براہِ کرم اپنے آخری عطیے کی تاریخ درج کریں۔","مهرباني ڪري پنهنجي آخري عطئي جي تاريخ داخل ڪريو."],
["Please answer every health screening question.","براہِ کرم صحت کی جانچ کے تمام سوالات کے جواب دیں۔","مهرباني ڪري صحت جي جاچ جي سڀني سوالن جا جواب ڏيو."],
["Please confirm the health screening declaration.","براہِ کرم صحت کی جانچ کے بیان کی تصدیق کریں۔","مهرباني ڪري صحت جي جاچ واري بيان جي تصديق ڪريو."],
["You are currently ineligible to donate blood.","آپ اس وقت خون عطیہ کرنے کے اہل نہیں ہیں۔","توهان هن وقت رت عطيو ڪرڻ جا اهل ناهيو."],
["Something went wrong while saving your donor profile.","آپ کا عطیہ دہندہ پروفائل محفوظ کرتے وقت کوئی مسئلہ پیش آیا۔","توهان جو عطيو ڏيندڙ پروفائل محفوظ ڪندي مسئلو پيش آيو."],
["Unable to load the donor directory.","عطیہ دہندگان کی فہرست لوڈ نہیں ہو سکی۔","عطيو ڏيندڙن جي فهرست لوڊ نه ٿي سگهي."],
["Check the blood group, location, hospital, contact number, requested units, and future deadline.","بلڈ گروپ، مقام، ہسپتال، رابطہ نمبر، مطلوبہ یونٹس اور مستقبل کی آخری تاریخ چیک کریں۔","رت جو گروپ، هنڌ، اسپتال، رابطو نمبر، گهربل يونٽ ۽ مستقبل جي آخري تاريخ چيڪ ڪريو."],
["You can have a maximum of 3 active blood requests. Complete or cancel an existing request before creating another.","آپ زیادہ سے زیادہ 3 فعال خون کی درخواستیں رکھ سکتے ہیں۔ نئی درخواست بنانے سے پہلے موجودہ درخواست مکمل یا منسوخ کریں۔","توهان وڌ ۾ وڌ 3 فعال رت جون درخواستون رکي سگهو ٿا. نئين درخواست ٺاهڻ کان اڳ موجوده درخواست مڪمل يا رد ڪريو."],
["Unable to create the blood request.","خون کی درخواست نہیں بنائی جا سکی۔","رت جي درخواست ٺاهي نه سگهي."],
["You can only cancel your own blood requests.","آپ صرف اپنی خون کی درخواستیں منسوخ کر سکتے ہیں۔","توهان صرف پنهنجون رت جون درخواستون رد ڪري سگهو ٿا."],
["Your blood request was cancelled. Received units and donation history were preserved, and pending donor acceptances were released.","آپ کی خون کی درخواست منسوخ کر دی گئی۔ موصولہ یونٹس اور عطیے کی تاریخ محفوظ رکھی گئی، جبکہ زیرِ التوا عطیہ دہندگان کی قبولیتیں ختم کر دی گئیں۔","توهان جي رت جي درخواست رد ڪئي وئي. مليل يونٽ ۽ عطئي جي تاريخ محفوظ رکي وئي، جڏهن ته انتظار واريون قبوليتون ختم ڪيون ويون."],
["Select the donor profile you want to use for this match.","اس میچ کے لیے استعمال ہونے والا عطیہ دہندہ پروفائل منتخب کریں۔","هن ميچ لاءِ استعمال ٿيندڙ عطيو ڏيندڙ پروفائل چونڊيو."],
["The selected donor profile does not belong to your account.","منتخب کردہ عطیہ دہندہ پروفائل آپ کے اکاؤنٹ سے تعلق نہیں رکھتا۔","چونڊيل عطيو ڏيندڙ پروفائل توهان جي اڪائونٽ سان لاڳاپيل ناهي."],
["You cannot accept your own blood request.","آپ اپنی خون کی درخواست خود قبول نہیں کر سکتے۔","توهان پنهنجي رت جي درخواست پاڻ قبول نٿا ڪري سگهو."],
["This request is no longer available.","یہ درخواست اب دستیاب نہیں ہے۔","هي درخواست هاڻي موجود ناهي."],
["This request has expired because its required deadline has passed. It can no longer be accepted.","اس درخواست کی میعاد ختم ہو چکی ہے کیونکہ مطلوبہ آخری وقت گزر گیا ہے۔ اب اسے قبول نہیں کیا جا سکتا۔","هن درخواست جي مدت ختم ٿي وئي آهي ڇاڪاڻ ته گهربل آخري وقت گذري ويو آهي. هاڻي ان کي قبول نٿو ڪري سگهجي."],
["Request accepted. Your match is active and ready for coordination.","درخواست قبول ہو گئی۔ آپ کا میچ فعال ہے اور رابطہ کاری کے لیے تیار ہے۔","درخواست قبول ٿي وئي. توهان جو ميچ فعال آهي ۽ سهڪار لاءِ تيار آهي."],
["Unable to accept this request.","یہ درخواست قبول نہیں کی جا سکی۔","هي درخواست قبول نه ٿي سگهي."],
["Create an active blood request first, then return to the donor directory to request this donor.","پہلے خون کی ایک فعال درخواست بنائیں، پھر اس عطیہ دہندہ سے درخواست کرنے کے لیے ڈونر ڈائریکٹری میں واپس آئیں۔","پهرين فعال رت جي درخواست ٺاهيو، پوءِ هن عطيو ڏيندڙ کي درخواست ڏيڻ لاءِ ڊونر ڊائريڪٽري ڏانهن واپس اچو."],
["This donor profile is unavailable.","یہ عطیہ دہندہ پروفائل دستیاب نہیں ہے۔","هي عطيو ڏيندڙ پروفائل موجود ناهي."],
["This donor profile already has an active match or invitation.","اس عطیہ دہندہ پروفائل کا پہلے ہی ایک فعال میچ یا دعوت موجود ہے۔","هن عطيو ڏيندڙ پروفائل جو اڳ ۾ ئي فعال ميچ يا دعوت موجود آهي."],
["This donor is no longer eligible or compatible with your active request.","یہ عطیہ دہندہ اب آپ کی فعال درخواست کے لیے اہل یا موزوں نہیں ہے۔","هي عطيو ڏيندڙ هاڻي توهان جي فعال درخواست لاءِ اهل يا مناسب ناهي."],
["All units for your active request are already matched.","آپ کی فعال درخواست کے تمام یونٹس پہلے ہی میچ ہو چکے ہیں۔","توهان جي فعال درخواست جا سڀ يونٽ اڳ ۾ ئي ميچ ٿي چڪا آهن."],
["You have already requested this donor for this blood request.","آپ اس خون کی درخواست کے لیے اس عطیہ دہندہ سے پہلے ہی درخواست کر چکے ہیں۔","توهان هن رت جي درخواست لاءِ هن عطيو ڏيندڙ کي اڳ ۾ ئي درخواست موڪلي آهي."],
["Donor selected. Your match is now active.","عطیہ دہندہ منتخب ہو گیا۔ آپ کا میچ اب فعال ہے۔","عطيو ڏيندڙ چونڊيو ويو. توهان جو ميچ هاڻي فعال آهي."],
["Unable to start this match right now.","اس وقت یہ میچ شروع نہیں کیا جا سکا۔","هن وقت هي ميچ شروع نه ٿي سگهيو."],
["Your donor profile is not currently eligible to accept this invitation.","آپ کا عطیہ دہندہ پروفائل اس وقت یہ دعوت قبول کرنے کا اہل نہیں ہے۔","توهان جو عطيو ڏيندڙ پروفائل هن وقت هي دعوت قبول ڪرڻ جو اهل ناهي."],
["The blood request has expired or is already fulfilled.","خون کی درخواست کی میعاد ختم ہو چکی ہے یا یہ پہلے ہی پوری ہو گئی ہے۔","رت جي درخواست جي مدت ختم ٿي وئي آهي يا اها اڳ ۾ ئي مڪمل ٿي چڪي آهي."],
["You already have another active match. Complete it before accepting this invitation.","آپ کا پہلے ہی ایک دوسرا فعال میچ موجود ہے۔ یہ دعوت قبول کرنے سے پہلے اسے مکمل کریں۔","توهان جو اڳ ۾ ئي ٻيو فعال ميچ آهي. هي دعوت قبول ڪرڻ کان اڳ ان کي مڪمل ڪريو."],
["No unreserved units remain for this request.","اس درخواست کے لیے کوئی غیر مختص یونٹ باقی نہیں۔","هن درخواست لاءِ ڪو غير مختص يونٽ باقي ناهي."],
["Invitation accepted. Your match is now active.","دعوت قبول ہو گئی۔ آپ کا میچ اب فعال ہے۔","دعوت قبول ٿي وئي. توهان جو ميچ هاڻي فعال آهي."],
["Only the matched donor can cancel this acceptance.","صرف میچ ہونے والا عطیہ دہندہ اس قبولیت کو منسوخ کر سکتا ہے۔","صرف ميچ ٿيل عطيو ڏيندڙ هن قبوليت کي رد ڪري سگهي ٿو."],
["Only a pending, unconfirmed acceptance can be cancelled.","صرف زیرِ التوا اور غیر مصدقہ قبولیت منسوخ کی جا سکتی ہے۔","صرف انتظار واري ۽ غير تصديق ٿيل قبوليت رد ڪري سگهجي ٿي."],
["Your pending acceptance has been cancelled.","آپ کی زیرِ التوا قبولیت منسوخ کر دی گئی ہے۔","توهان جي انتظار واري قبوليت رد ڪئي وئي آهي."],
["Only the requester can process this match.","صرف درخواست گزار اس میچ پر کارروائی کر سکتا ہے۔","صرف درخواست ڪندڙ هن ميچ تي عمل ڪري سگهي ٿو."],
["This match has already been processed.","اس میچ پر پہلے ہی کارروائی ہو چکی ہے۔","هن ميچ تي اڳ ۾ ئي عمل ٿي چڪو آهي."],
["Match acceptance rejected.","میچ کی قبولیت مسترد کر دی گئی۔","ميچ جي قبوليت رد ڪئي وئي."],
["Match confirmed successfully.","میچ کی کامیابی سے تصدیق ہو گئی۔","ميچ جي ڪاميابي سان تصديق ٿي وئي."],
["Write a message before sending.","بھیجنے سے پہلے پیغام لکھیں۔","موڪلڻ کان اڳ پيغام لکو."],
["This match is unavailable or you do not have access.","یہ میچ دستیاب نہیں یا آپ کو اس تک رسائی حاصل نہیں۔","هي ميچ موجود ناهي يا توهان کي ان تائين رسائي ناهي."],
["Chat is available only while this match is active.","چیٹ صرف اس وقت دستیاب ہے جب میچ فعال ہو۔","چيٽ صرف تڏهن موجود آهي جڏهن ميچ فعال هجي."],
["Unable to send your message. Please try again.","آپ کا پیغام نہیں بھیجا جا سکا۔ براہِ کرم دوبارہ کوشش کریں۔","توهان جو پيغام موڪلي نه سگهيو. مهرباني ڪري ٻيهر ڪوشش ڪريو."],
["Enter a valid donation date and number of units.","عطیے کی درست تاریخ اور یونٹس کی تعداد درج کریں۔","عطئي جي صحيح تاريخ ۽ يونٽن جو تعداد داخل ڪريو."],
["Only the requester can report the donation received.","صرف درخواست گزار موصول ہونے والے عطیے کی رپورٹ دے سکتا ہے۔","صرف درخواست ڪندڙ وصول ٿيل عطئي جي رپورٽ ڏئي سگهي ٿو."],
["Only an active confirmed match can have a donation report.","صرف فعال اور تصدیق شدہ میچ کے لیے عطیے کی رپورٹ دی جا سکتی ہے۔","صرف فعال ۽ تصديق ٿيل ميچ لاءِ عطئي جي رپورٽ ڏئي سگهجي ٿي."],
["Reported units exceed the pledged or remaining units.","رپورٹ کردہ یونٹس وعدہ کردہ یا باقی یونٹس سے زیادہ ہیں۔","رپورٽ ڪيل يونٽ واعدو ڪيل يا باقي يونٽن کان وڌيڪ آهن."],
["A completed donation report already exists for this match.","اس میچ کے لیے عطیے کی مکمل رپورٹ پہلے ہی موجود ہے۔","هن ميچ لاءِ عطئي جي مڪمل رپورٽ اڳ ۾ ئي موجود آهي."],
["Donation recorded. A copy is now saved in the donor's profile history.","عطیہ درج ہو گیا۔ اس کی ایک نقل اب عطیہ دہندہ کے پروفائل کی تاریخ میں محفوظ ہے۔","عطيو درج ٿي ويو. ان جي هڪ ڪاپي هاڻي عطيو ڏيندڙ جي پروفائل جي تاريخ ۾ محفوظ آهي."],
["Unable to record this donation right now.","اس وقت یہ عطیہ درج نہیں کیا جا سکا۔","هن وقت هي عطيو درج نه ٿي سگهيو."],
["Enter the actual number of units received.","موصول ہونے والے یونٹس کی اصل تعداد درج کریں۔","وصول ٿيل يونٽن جو اصل تعداد داخل ڪريو."],
["Only the requester can confirm receipt.","صرف درخواست گزار وصولی کی تصدیق کر سکتا ہے۔","صرف درخواست ڪندڙ وصولي جي تصديق ڪري سگهي ٿو."],
["This donation has already been confirmed.","اس عطیے کی پہلے ہی تصدیق ہو چکی ہے۔","هن عطئي جي اڳ ۾ ئي تصديق ٿي چڪي آهي."],
["This match is not awaiting receipt confirmation.","یہ میچ وصولی کی تصدیق کا منتظر نہیں ہے۔","هي ميچ وصولي جي تصديق جو منتظر ناهي."],
["You cannot confirm more units than the donor reported.","آپ عطیہ دہندہ کی رپورٹ کردہ تعداد سے زیادہ یونٹس کی تصدیق نہیں کر سکتے۔","توهان عطيو ڏيندڙ جي رپورٽ ڪيل تعداد کان وڌيڪ يونٽن جي تصديق نٿا ڪري سگهو."],
["The confirmed quantity must be greater than zero.","تصدیق شدہ مقدار صفر سے زیادہ ہونی چاہیے۔","تصديق ٿيل مقدار صفر کان وڌيڪ هجڻ گهرجي."],
["Receipt confirmed. Request units have been updated.","وصولی کی تصدیق ہو گئی۔ درخواست کے یونٹس اپ ڈیٹ کر دیے گئے ہیں۔","وصولي جي تصديق ٿي وئي. درخواست جا يونٽ اپڊيٽ ڪيا ويا آهن."],
["Unable to confirm receipt.","وصولی کی تصدیق نہیں کی جا سکی۔","وصولي جي تصديق نه ٿي سگهي."],
["Profile updated successfully.","پروفائل کامیابی سے اپ ڈیٹ ہو گیا۔","پروفائل ڪاميابي سان اپڊيٽ ٿي ويو."],
["Unable to update profile. The CNIC, email, or phone may already be registered.","پروفائل اپ ڈیٹ نہیں ہو سکا۔ ممکن ہے CNIC، ای میل یا فون پہلے سے رجسٹر ہو۔","پروفائل اپڊيٽ نه ٿي سگهيو. ٿي سگهي ٿو CNIC، اي ميل يا فون اڳ ۾ رجسٽر ٿيل هجي."],
["Please enter your name.","براہِ کرم اپنا نام درج کریں۔","مهرباني ڪري پنهنجو نالو داخل ڪريو."],
["Enter an email address or phone number.","ای میل ایڈریس یا فون نمبر درج کریں۔","اي ميل پتو يا فون نمبر داخل ڪريو."],
["Enter a valid email address.","درست ای میل ایڈریس درج کریں۔","صحيح اي ميل پتو داخل ڪريو."],
["Enter a valid phone number.","درست فون نمبر درج کریں۔","صحيح فون نمبر داخل ڪريو."],
["Enter a valid 13-digit CNIC number.","درست 13 ہندسوں والا CNIC نمبر درج کریں۔","صحيح 13 انگن وارو CNIC نمبر داخل ڪريو."],
["Password must be between 8 and 128 characters.","پاس ورڈ 8 سے 128 حروف کے درمیان ہونا چاہیے۔","پاسورڊ 8 کان 128 اکرن جي وچ ۾ هجڻ گهرجي."],
["Account created successfully. Please log in.","اکاؤنٹ کامیابی سے بن گیا۔ براہِ کرم لاگ اِن کریں۔","اڪائونٽ ڪاميابي سان ٺهي ويو. مهرباني ڪري لاگ اِن ڪريو."],
["Unable to create account. Please check your information.","اکاؤنٹ نہیں بن سکا۔ براہِ کرم اپنی معلومات چیک کریں۔","اڪائونٽ ٺهي نه سگهيو. مهرباني ڪري پنهنجي معلومات چيڪ ڪريو."],
["Enter your email/phone and password.","اپنا ای میل/فون اور پاس ورڈ درج کریں۔","پنهنجو اي ميل/فون ۽ پاسورڊ داخل ڪريو."],
["Unable to sign in right now. Please try again.","اس وقت سائن اِن نہیں ہو سکا۔ براہِ کرم دوبارہ کوشش کریں۔","هن وقت سائن اِن نه ٿي سگهيو. مهرباني ڪري ٻيهر ڪوشش ڪريو."],
["Invalid user name.","صارف کا نام درست نہیں۔","استعمال ڪندڙ جو نالو صحيح ناهي."],
["Invalid password.","پاس ورڈ درست نہیں۔","پاسورڊ صحيح ناهي."],
["Login successful.","کامیابی سے لاگ اِن ہو گیا۔","ڪاميابي سان لاگ اِن ٿيو."],
["You have been logged out.","آپ لاگ آؤٹ ہو چکے ہیں۔","توهان لاگ آئوٽ ٿي چڪا ہیں."]
];
D.Urdu["Sign In"]="سائن اِن";
D.Sindhi["Sign In"]="سائن اِن";
D.Urdu["Sign Up"]="سائن اَپ";
D.Sindhi["Sign Up"]="سائن اپ";
D.Urdu["Create Account"]="اکاؤنٹ بنائیں";
D.Sindhi["Create Account"]="اڪائونٽ ٺاهيو";
D.Urdu["Show"]="دکھائیں";
D.Sindhi["Show"]="ڏيکاريو";
D.Urdu["Hide"]="چھپائیں";
D.Sindhi["Hide"]="لڪايو";
D.Urdu["Already have an account?"]="کیا آپ کا پہلے سے اکاؤنٹ ہے؟";
D.Sindhi["Already have an account?"]="ڇا توهان وٽ اڳ ۾ اڪائونٽ آهي؟";
D.Urdu["Your account access is protected."]="آپ کے اکاؤنٹ تک رسائی محفوظ ہے۔";
D.Sindhi["Your account access is protected."]="توهان جي اڪائونٽ تائين رسائي محفوظ آهي.";
D.Urdu["Your CNIC and account credentials are private."]="آپ کا CNIC اور اکاؤنٹ کی معلومات نجی ہیں۔";
D.Sindhi["Your CNIC and account credentials are private."]="توهان جو CNIC ۽ اڪائونٽ جا تفصيل ذاتي آهن.";
D.Urdu["Activity Centre"]="سرگرمیوں کا مرکز";D.Sindhi["Activity Centre"]="سرگرمين جو مرڪز";
D.Urdu["unread"]="غیر پڑھی ہوئی";D.Sindhi["unread"]="اڻپڙهيل";
D.Urdu["total"]="کل";D.Sindhi["total"]="ڪل";
D.Urdu["New blood request"]="خون کی نئی درخواست";D.Sindhi["New blood request"]="رت جي نئين درخواست";
D.Urdu["Match request found"]="میچ کی درخواست مل گئی";D.Sindhi["Match request found"]="ميچ جي درخواست ملي";
D.Urdu["Your blood request was created"]="آپ کی خون کی درخواست بن گئی";D.Sindhi["Your blood request was created"]="توهان جي رت جي درخواست ٺهي وئي";
D.Urdu["Compatible donor found"]="موزوں عطیہ دہندہ مل گیا";D.Sindhi["Compatible donor found"]="مناسب عطيو ڏيندڙ مليو";
D.Urdu["New donor invitation"]="عطیہ دہندہ کی نئی دعوت";D.Sindhi["New donor invitation"]="عطيو ڏيندڙ جي نئين دعوت";
D.Urdu["Donor accepted your request"]="عطیہ دہندہ نے آپ کی درخواست قبول کر لی";D.Sindhi["Donor accepted your request"]="عطيو ڏيندڙ توهان جي درخواست قبول ڪئي";
D.Urdu["Your acceptance is waiting"]="آپ کی قبولیت منتظر ہے";D.Sindhi["Your acceptance is waiting"]="توهان جي قبوليت انتظار ۾ آهي";
D.Urdu["Match confirmed"]="میچ کی تصدیق ہو گئی";D.Sindhi["Match confirmed"]="ميچ جي تصديق ٿي وئي";
D.Urdu["Private chat message"]="نجی چیٹ کا پیغام";D.Sindhi["Private chat message"]="ذاتي چيٽ جو پيغام";
D.Urdu["Match rejected"]="میچ مسترد ہو گیا";D.Sindhi["Match rejected"]="ميچ رد ٿي ويو";
D.Urdu["Match cancelled"]="میچ منسوخ ہو گیا";D.Sindhi["Match cancelled"]="ميچ رد ٿي ويو";
D.Urdu["Donation receipt confirmed"]="عطیے کی وصولی کی تصدیق ہو گئی";D.Sindhi["Donation receipt confirmed"]="عطئي جي وصولي جي تصديق ٿي وئي";
D.Urdu["Donor eligibility update"]="عطیہ دہندہ کی اہلیت کی تازہ معلومات";D.Sindhi["Donor eligibility update"]="عطيو ڏيندڙ جي اهليت بابت تازه معلومات";
D.Urdu["Your notifications"]="آپ کی اطلاعات";D.Sindhi["Your notifications"]="توهان جون اطلاعون";
D.Urdu["Notifications"]="اطلاعات";D.Sindhi["Notifications"]="اطلاعون";
D.Urdu["Notification"]="اطلاع";D.Sindhi["Notification"]="اطلاع";
D.Urdu["Blood Donor Directory"]="خون کے عطیہ دہندگان کی فہرست";D.Sindhi["Blood Donor Directory"]="رت جي عطيو ڏيندڙن جي فهرست";
D.Urdu["Open navigation menu"]="نیویگیشن مینو کھولیں";D.Sindhi["Open navigation menu"]="نيويگيشن مينيو کوليو";
D.Urdu["Close navigation menu"]="نیویگیشن مینو بند کریں";D.Sindhi["Close navigation menu"]="نيويگيشن مينيو بند ڪريو";
D.Urdu["Back to Dashboard"]="ڈیش بورڈ پر واپس جائیں";D.Sindhi["Back to Dashboard"]="ڊيش بورڊ ڏانهن واپس وڃو";
D.Urdu["Back to Emergency Request"]="ہنگامی درخواست پر واپس جائیں";D.Sindhi["Back to Emergency Request"]="هنگامي درخواست ڏانهن واپس وڃو";
D.Urdu["Explore blood group"]="بلڈ گروپ دیکھیں";D.Sindhi["Explore blood group"]="رت جو گروپ ڏسو";
D.Urdu["Compatible donor groups:"]="موزوں عطیہ دہندگان کے بلڈ گروپس:";D.Sindhi["Compatible donor groups:"]="مناسب عطيو ڏيندڙن جا رت جا گروپ:";
D.Urdu["Available compatible donors"]="دستیاب موزوں عطیہ دہندگان";D.Sindhi["Available compatible donors"]="موجود مناسب عطيو ڏيندڙ";
D.Urdu["Open blood requests"]="کھلی خون کی درخواستیں";D.Sindhi["Open blood requests"]="کليل رت جون درخواستون";
D.Urdu["Urgency:"]="فوری نوعیت:";D.Sindhi["Urgency:"]="تڪڙ:";
D.Urdu["Location:"]="مقام:";D.Sindhi["Location:"]="هنڌ:";
D.Urdu["Hospital:"]="ہسپتال:";D.Sindhi["Hospital:"]="اسپتال:";
D.Urdu["Units remaining:"]="باقی یونٹس:";D.Sindhi["Units remaining:"]="باقي يونٽ:";
D.Urdu["Match status:"]="میچ کی حیثیت:";D.Sindhi["Match status:"]="ميچ جي حيثيت:";
D.Urdu["Donor:"]="عطیہ دہندہ:";D.Sindhi["Donor:"]="عطيو ڏيندڙ:";
D.Urdu["Requester:"]="درخواست گزار:";D.Sindhi["Requester:"]="درخواست ڪندڙ:";
D.Urdu["Contact details become available after the requester confirms this match."]="درخواست گزار کی جانب سے میچ کی تصدیق کے بعد رابطے کی تفصیلات دستیاب ہوں گی۔";D.Sindhi["Contact details become available after the requester confirms this match."]="درخواست ڪندڙ جي ميچ جي تصديق کان پوءِ رابطي جا تفصيل موجود ٿيندا.";
D.Urdu["Donation date"]="عطیے کی تاریخ";D.Sindhi["Donation date"]="عطئي جي تاريخ";
D.Urdu["Units donated"]="عطیہ کیے گئے یونٹس";D.Sindhi["Units donated"]="عطيو ڪيل يونٽ";
D.Urdu["Report donation"]="عطیے کی رپورٹ";D.Sindhi["Report donation"]="عطئي جي رپورٽ";
D.Urdu["Date:"]="تاریخ:";D.Sindhi["Date:"]="تاريخ:";
D.Urdu["Units:"]="یونٹس:";D.Sindhi["Units:"]="يونٽ:";
D.Urdu["Request ID:"]="درخواست نمبر:";D.Sindhi["Request ID:"]="درخواست نمبر:";
D.Urdu["Receipt:"]="وصولی:";D.Sindhi["Receipt:"]="وصولي:";
D.Urdu["Email:"]="ای میل:";D.Sindhi["Email:"]="اي ميل:";
D.Urdu["Phone:"]="فون:";D.Sindhi["Phone:"]="فون:";
D.Urdu["CNIC:"]="شناختی کارڈ:";D.Sindhi["CNIC:"]="شناختي ڪارڊ:";
D.Urdu["Blood group:"]="بلڈ گروپ:";D.Sindhi["Blood group:"]="رت جو گروپ:";
D.Urdu["Age:"]="عمر:";D.Sindhi["Age:"]="عمر:";
D.Urdu["Status:"]="حیثیت:";D.Sindhi["Status:"]="حيثيت:";
D.Urdu["Created:"]="تخلیق کی تاریخ:";D.Sindhi["Created:"]="ٺهڻ جي تاريخ:";
D.Urdu["Received units:"]="موصولہ یونٹس:";D.Sindhi["Received units:"]="مليل يونٽ:";
D.Urdu["Remaining units:"]="باقی یونٹس:";D.Sindhi["Remaining units:"]="باقي يونٽ:";
D.Urdu["Needed by:"]="ضرورت کی تاریخ:";D.Sindhi["Needed by:"]="گهربل تاريخ:";
D.Urdu["Open Private Chat"]="نجی چیٹ کھولیں";D.Sindhi["Open Private Chat"]="ذاتي چيٽ کوليو";
D.Urdu["View Potential Matches"]="ممکنہ میچز دیکھیں";D.Sindhi["View Potential Matches"]="ممڪن ميچ ڏسو";
D.Urdu["Open Potential Matches"]="ممکنہ میچز کھولیں";D.Sindhi["Open Potential Matches"]="ممڪن ميچ کوليو";
D.Urdu["View Available Requests"]="دستیاب درخواستیں دیکھیں";D.Sindhi["View Available Requests"]="موجود درخواستون ڏسو";
D.Urdu["View My Requests"]="میری درخواستیں دیکھیں";D.Sindhi["View My Requests"]="منهنجون درخواستون ڏسو";
D.Urdu["View Donor Profile"]="عطیہ دہندہ کا پروفائل دیکھیں";D.Sindhi["View Donor Profile"]="عطيو ڏيندڙ جو پروفائل ڏسو";
D.Urdu["Open Dashboard"]="ڈیش بورڈ کھولیں";D.Sindhi["Open Dashboard"]="ڊيش بورڊ کوليو";
D.Urdu["Mark as read"]="پڑھا ہوا نشان زد کریں";D.Sindhi["Mark as read"]="پڙهيل طور نشان لڳايو";
D.Urdu["Read"]="پڑھی ہوئی";D.Sindhi["Read"]="پڙهيل";
D.Urdu["NEW"]="نیا";D.Sindhi["NEW"]="نئون";
D.Urdu["Back to Donor Directory"]="عطیہ دہندگان کی فہرست پر واپس جائیں";D.Sindhi["Back to Donor Directory"]="عطيو ڏيندڙن جي فهرست ڏانهن واپس وڃو";
D.Urdu["Available"]="دستیاب";D.Sindhi["Available"]="موجود";
D.Urdu["Not Available"]="دستیاب نہیں";D.Sindhi["Not Available"]="موجود ناهي";
D.Urdu["Pending"]="زیرِ التوا";D.Sindhi["Pending"]="انتظار ۾";
D.Urdu["Fulfilled"]="مکمل";D.Sindhi["Fulfilled"]="مڪمل";
D.Urdu["Cancelled"]="منسوخ";D.Sindhi["Cancelled"]="رد ٿيل";
D.Urdu["Expired"]="میعاد ختم";D.Sindhi["Expired"]="مدو پورو";
D.Urdu["Confirmed"]="تصدیق شدہ";D.Sindhi["Confirmed"]="تصديق ٿيل";
D.Urdu["Reported"]="رپورٹ شدہ";D.Sindhi["Reported"]="رپورٽ ٿيل";
D.Urdu["Accepted"]="قبول شدہ";D.Sindhi["Accepted"]="قبول ٿيل";
D.Urdu["Rejected"]="مسترد";D.Sindhi["Rejected"]="رد ٿيل";
D.Urdu["Completed"]="مکمل";D.Sindhi["Completed"]="مڪمل";
D.Urdu["Active"]="فعال";D.Sindhi["Active"]="فعال";
D.Urdu["Invited"]="دعوت دی گئی";D.Sindhi["Invited"]="دعوت ڏنل";
D.Urdu["Eligible"]="اہل";D.Sindhi["Eligible"]="اهل";
D.Urdu["Not Eligible"]="اہل نہیں";D.Sindhi["Not Eligible"]="اهل ناهي";
D.Urdu["New emergency blood request:"]="خون کی نئی ہنگامی درخواست:";D.Sindhi["New emergency blood request:"]="رت جي نئين هنگامي درخواست:";
D.Urdu["New normal blood request:"]="خون کی نئی عام درخواست:";D.Sindhi["New normal blood request:"]="رت جي نئين عام درخواست:";
D.Urdu["location:"]="مقام:";D.Sindhi["location:"]="هنڌ:";
D.Urdu["Blood needed by:"]="خون درکار ہونے کی آخری تاریخ:";D.Sindhi["Blood needed by:"]="رت گهربل ٿيڻ جي آخري تاريخ:";
D.Urdu["Pakistan time"]="پاکستان کا وقت";D.Sindhi["Pakistan time"]="پاڪستان جو وقت";
D.Urdu["is available for your"]="آپ کی درخواست کے لیے دستیاب ہے";D.Sindhi["is available for your"]="توهان جي درخواست لاءِ موجود آهي";
D.Urdu["blood request"]="خون کی درخواست";D.Sindhi["blood request"]="رت جي درخواست";
D.Urdu["has completed the 90-day"]="نے 90 دن کا وقفہ مکمل کر لیا ہے";D.Sindhi["has completed the 90-day"]="90 ڏينهن جو وقفو مڪمل ڪيو آهي";
D.Urdu["donation interval. Professional screening"]="عطیے کا وقفہ۔ طبی جانچ";D.Sindhi["donation interval. Professional screening"]="عطئي جو وقفو. طبي جاچ";
D.Urdu["is still required before donating."]="عطیہ دینے سے پہلے ابھی بھی ضروری ہے۔";D.Sindhi["is still required before donating."]="عطيو ڏيڻ کان اڳ اڃا به ضروري آهي.";
D.Urdu["is overdue."]="کی آخری تاریخ گزر چکی ہے۔";D.Sindhi["is overdue."]="جي آخري تاريخ گذري چڪي آهي.";
D.Urdu["unit(s) remain unfulfilled."]="یونٹس ابھی باقی ہیں۔";D.Sindhi["unit(s) remain unfulfilled."]="يونٽ اڃا باقي آهن.";
D.Urdu["has passed its deadline"]="کی آخری تاریخ گزر چکی ہے";D.Sindhi["has passed its deadline"]="جي آخري تاريخ گذري چڪي آهي";
D.Urdu["and is still incomplete. Please coordinate with the requester."]="اور ابھی نامکمل ہے۔ براہِ کرم درخواست گزار سے رابطہ کریں۔";D.Sindhi["and is still incomplete. Please coordinate with the requester."]="۽ اڃا نامڪمل آهي. مهرباني ڪري درخواست ڪندڙ سان رابطو ڪريو.";
D.Urdu["is the required deadline."]="مطلوبہ آخری وقت ہے۔";D.Sindhi["is the required deadline."]="گهربل آخري وقت آهي.";
D.Urdu["The blood request deadline passed before confirmation."]="تصدیق سے پہلے خون کی درخواست کی آخری تاریخ گزر گئی۔";D.Sindhi["The blood request deadline passed before confirmation."]="تصديق کان اڳ رت جي درخواست جي آخري تاريخ گذري وئي.";
D.Urdu["Your pending acceptance was cancelled."]="آپ کی زیرِ التوا قبولیت منسوخ کر دی گئی۔";D.Sindhi["Your pending acceptance was cancelled."]="توهان جي انتظار واري قبوليت رد ڪئي وئي.";
D.Urdu["Your blood request has expired because its deadline passed"]="آپ کی خون کی درخواست کی میعاد ختم ہو گئی کیونکہ آخری تاریخ گزر گئی";D.Sindhi["Your blood request has expired because its deadline passed"]="توهان جي رت جي درخواست جي مدت ختم ٿي وئي ڇاڪاڻ ته آخري تاريخ گذري وئي";
D.Urdu["or was missing. Any unconfirmed donor acceptances were cancelled."]="یا درج نہیں تھی۔ عطیہ دہندگان کی تمام غیر مصدقہ قبولیتیں منسوخ کر دی گئیں۔";D.Sindhi["or was missing. Any unconfirmed donor acceptances were cancelled."]="يا درج نه هئي. عطيو ڏيندڙن جون سڀ غير تصديق ٿيل قبوليتون رد ڪيون ويون.";
D.Urdu["A previous pending match could not be activated because the donor or request was no longer available."]="پہلا زیرِ التوا میچ فعال نہیں ہو سکا کیونکہ عطیہ دہندہ یا درخواست اب دستیاب نہیں تھی۔";D.Sindhi["A previous pending match could not be activated because the donor or request was no longer available."]="اڳوڻو انتظار وارو ميچ فعال نه ٿي سگهيو ڇاڪاڻ ته عطيو ڏيندڙ يا درخواست هاڻي موجود نه هئي.";
D.Urdu["Your previous pending match is now active."]="آپ کا پچھلا زیرِ التوا میچ اب فعال ہے۔";D.Sindhi["Your previous pending match is now active."]="توهان جو اڳوڻو انتظار وارو ميچ هاڻي فعال آهي.";
D.Urdu["Your blood request has been fully fulfilled."]="آپ کی خون کی درخواست مکمل طور پر پوری ہو گئی ہے۔";D.Sindhi["Your blood request has been fully fulfilled."]="توهان جي رت جي درخواست مڪمل ٿي وئي آهي.";
D.Urdu["has been fulfilled by other"]="دوسرے عطیات کے ذریعے پوری ہو گئی ہے";D.Sindhi["has been fulfilled by other"]="ٻين عطين ذريعي مڪمل ٿي وئي آهي";
D.Urdu["donation(s). Your undonated match has been released."]="عطیات۔ آپ کا غیر عطیہ شدہ میچ ختم کر دیا گیا ہے۔";D.Sindhi["donation(s). Your undonated match has been released."]="عطيا. توهان جو عطيو نه ٿيل ميچ ختم ڪيو ويو آهي.";
D.Urdu["Match Request Found:"]="میچ کے لیے درخواست مل گئی:";D.Sindhi["Match Request Found:"]="ميچ لاءِ درخواست ملي آهي:";
D.Urdu["blood request needs"]="خون کی درخواست کو درکار ہیں";D.Sindhi["blood request needs"]="رت جي درخواست کي گهربل آهن";
D.Urdu["Urgency:"]="فوری نوعیت:";D.Sindhi["Urgency:"]="تڪڙ:";
D.Urdu["Deadline:"]="آخری وقت:";D.Sindhi["Deadline:"]="آخري وقت:";
D.Urdu["Your blood request has been created."]="آپ کی خون کی درخواست بن گئی ہے۔";D.Sindhi["Your blood request has been created."]="توهان جي رت جي درخواست ٺهي وئي آهي.";
D.Urdu["has been created."]="بنائی گئی ہے۔";D.Sindhi["has been created."]="ٺاهي وئي آهي.";
D.Urdu["Donor availability changed to"]="عطیہ دہندہ کی دستیابی تبدیل ہو کر";D.Sindhi["Donor availability changed to"]="عطيو ڏيندڙ جي دستيابي تبديل ٿي";
D.Urdu["Your profile is saved, but you are temporarily unavailable"]="آپ کا پروفائل محفوظ ہے، لیکن آپ عارضی طور پر دستیاب نہیں ہیں";D.Sindhi["Your profile is saved, but you are temporarily unavailable"]="توهان جو پروفائل محفوظ آهي، پر توهان عارضي طور موجود ناهيو";
D.Urdu["because fewer than 90 days have passed since your last donation."]="کیونکہ آپ کے آخری عطیے کے بعد 90 دن مکمل نہیں ہوئے۔";D.Sindhi["because fewer than 90 days have passed since your last donation."]="ڇاڪاڻ ته توهان جي آخري عطئي کان 90 ڏينهن پورا نه ٿيا آهن.";
D.Urdu["Blood request created successfully."]="خون کی درخواست کامیابی سے بن گئی۔";D.Sindhi["Blood request created successfully."]="رت جي درخواست ڪاميابي سان ٺهي وئي.";
D.Urdu["Your request is now matched with donor"]="آپ کی درخواست کا میچ اب عطیہ دہندہ سے ہو گیا ہے";D.Sindhi["Your request is now matched with donor"]="توهان جي درخواست جو ميچ هاڻي عطيو ڏيندڙ سان ٿي ويو آهي";
D.Urdu["The match is active and ready for coordination."]="میچ فعال ہے اور رابطہ کاری کے لیے تیار ہے۔";D.Sindhi["The match is active and ready for coordination."]="ميچ فعال آهي ۽ سهڪار لاءِ تيار آهي.";
D.Urdu["The requester cancelled the remaining open units for"]="درخواست گزار نے باقی کھلے یونٹس منسوخ کر دیے ہیں";D.Sindhi["The requester cancelled the remaining open units for"]="درخواست ڪندڙ باقي کليل يونٽ رد ڪري ڇڏيا آهن";
D.Urdu["Your reported donation remains active for receipt confirmation."]="آپ کی رپورٹ شدہ عطیہ وصولی کی تصدیق کے لیے فعال ہے۔";D.Sindhi["Your reported donation remains active for receipt confirmation."]="توهان جو رپورٽ ڪيل عطيو وصولي جي تصديق لاءِ فعال آهي.";
D.Urdu["New"]="نیا";D.Sindhi["New"]="نئون";
D.Urdu["NEW"]="نیا";D.Sindhi["NEW"]="نئون";
D.Urdu["The Blood Donor & Emergency Request Network helps connect people seeking blood with potential donors through a coordinated digital platform."]="بلڈ ڈونر اور ہنگامی درخواست نیٹ ورک ایک مربوط ڈیجیٹل پلیٹ فارم کے ذریعے خون تلاش کرنے والے افراد کو ممکنہ عطیہ دہندگان سے جوڑتا ہے۔";D.Sindhi["The Blood Donor & Emergency Request Network helps connect people seeking blood with potential donors through a coordinated digital platform."]="رت جي عطيو ڏيندڙ ۽ هنگامي درخواست نيٽ ورڪ هڪ منظم ڊجيٽل پليٽ فارم ذريعي رت ڳوليندڙ ماڻهن کي ممڪن عطيو ڏيندڙن سان ڳنڍي ٿو.";
D.Urdu["One connected network"]="ایک مربوط نیٹ ورک";D.Sindhi["One connected network"]="هڪ ڳنڍيل نيٽ ورڪ";
D.Urdu["Supporting donor discovery, emergency requests and donation coordination."]="عطیہ دہندگان کی تلاش، ہنگامی درخواستوں اور عطیے کی رابطہ کاری میں مدد۔";D.Sindhi["Supporting donor discovery, emergency requests and donation coordination."]="عطيو ڏيندڙن جي ڳولا، هنگامي درخواستن ۽ عطئي جي سهڪار ۾ مدد.";
D.Urdu["A coordinated digital network for donor discovery, emergency blood requests, controlled matching, direct communication and donation receipt tracking."]="عطیہ دہندگان کی تلاش، ہنگامی خون کی درخواستوں، منظم میچنگ، براہِ راست رابطے اور عطیے کی وصولی کی نگرانی کے لیے ایک مربوط ڈیجیٹل نیٹ ورک۔";D.Sindhi["A coordinated digital network for donor discovery, emergency blood requests, controlled matching, direct communication and donation receipt tracking."]="عطيو ڏيندڙن جي ڳولا، هنگامي رت جي درخواستن، منظم ميچنگ، سڌي رابطي ۽ عطئي جي وصولي جي نگراني لاءِ هڪ منظم ڊجيٽل نيٽ ورڪ.";
D.Urdu["Our mission is to simplify the process of finding potential blood donors and coordinating emergency blood requests."]="ہمارا مقصد ممکنہ خون کے عطیہ دہندگان تلاش کرنے اور ہنگامی خون کی درخواستوں میں رابطہ کاری کے عمل کو آسان بنانا ہے۔";D.Sindhi["Our mission is to simplify the process of finding potential blood donors and coordinating emergency blood requests."]="اسان جو مقصد ممڪن رت جا عطيو ڏيندڙ ڳولڻ ۽ هنگامي رت جي درخواستن ۾ سهڪار جي عمل کي آسان بڻائڻ آهي.";
D.Urdu["We aim to provide a structured alternative to scattered phone calls and social media messages."]="ہم بکھری ہوئی فون کالز اور سوشل میڈیا پیغامات کے بجائے ایک منظم متبادل فراہم کرنا چاہتے ہیں۔";D.Sindhi["We aim to provide a structured alternative to scattered phone calls and social media messages."]="اسان فون ڪالن ۽ سوشل ميڊيا پيغامن جي بدران هڪ منظم متبادل مهيا ڪرڻ چاهيون ٿا.";
D.Urdu["We envision a connected community where donors and people seeking blood can find relevant information and coordinate assistance through a reliable and accessible platform."]="ہم ایک ایسی مربوط کمیونٹی کا تصور رکھتے ہیں جہاں عطیہ دہندگان اور خون تلاش کرنے والے افراد قابلِ اعتماد اور قابلِ رسائی پلیٹ فارم کے ذریعے متعلقہ معلومات حاصل کر سکیں اور مدد میں رابطہ کاری کر سکیں۔";D.Sindhi["We envision a connected community where donors and people seeking blood can find relevant information and coordinate assistance through a reliable and accessible platform."]="اسان اهڙي ڳنڍيل ڪميونٽي جو تصور ڪريون ٿا جتي عطيو ڏيندڙ ۽ رت ڳوليندڙ ماڻهو ڀروسي جوڳي ۽ آسان پليٽ فارم ذريعي لاڳاپيل معلومات حاصل ڪري ۽ مدد جو بندوبست ڪري سگهن.";
D.Urdu["The platform brings important blood donation coordination activities together."]="یہ پلیٹ فارم خون کے عطیے سے متعلق اہم رابطہ کاری کے کام ایک جگہ فراہم کرتا ہے۔";D.Sindhi["The platform brings important blood donation coordination activities together."]="هي پليٽ فارم رت جي عطئي سان لاڳاپيل اهم سهڪاري ڪمن کي هڪ هنڌ گڏ ڪري ٿو.";
D.Urdu["You can register as a donor or participate as a requester."]="آپ عطیہ دہندہ کے طور پر رجسٹر ہو سکتے ہیں یا درخواست گزار کے طور پر حصہ لے سکتے ہیں۔";D.Sindhi["You can register as a donor or participate as a requester."]="توهان عطيو ڏيندڙ طور رجسٽر ٿي سگهو ٿا يا درخواست ڪندڙ طور حصو وٺي سگهو ٿا.";
D.Urdu["Explore compatible blood groups, register as a donor, or create an emergency request with the required blood units and hospital information."]="موزوں بلڈ گروپس دیکھیں، عطیہ دہندہ کے طور پر رجسٹر ہوں، یا مطلوبہ یونٹس اور ہسپتال کی معلومات کے ساتھ ہنگامی درخواست بنائیں۔";D.Sindhi["Explore compatible blood groups, register as a donor, or create an emergency request with the required blood units and hospital information."]="مناسب رت جا گروپ ڏسو، عطيو ڏيندڙ طور رجسٽر ٿيو، يا گهربل يونٽن ۽ اسپتال جي معلومات سان هنگامي درخواست ٺاهيو.";
D.Urdu["Donors accept requests, requesters confirm matches, and both parties track donation and receipt progress."]="عطیہ دہندگان درخواستیں قبول کرتے ہیں، درخواست گزار میچ کی تصدیق کرتے ہیں، اور دونوں فریق عطیے اور وصولی کی پیش رفت دیکھتے ہیں۔";D.Sindhi["Donors accept requests, requesters confirm matches, and both parties track donation and receipt progress."]="عطيو ڏيندڙ درخواستون قبول ڪن ٿا، درخواست ڪندڙ ميچ جي تصديق ڪن ٿا، ۽ ٻئي ڌريون عطئي ۽ وصولي جي اڳڀرائي ڏسن ٿيون.";
D.Urdu["Request: A requester creates a blood request and specifies the required blood group and units."]="درخواست: درخواست گزار خون کی درخواست بناتا ہے اور مطلوبہ بلڈ گروپ اور یونٹس بتاتا ہے۔";D.Sindhi["Request: A requester creates a blood request and specifies the required blood group and units."]="درخواست: درخواست ڪندڙ رت جي درخواست ٺاهي گهربل رت جو گروپ ۽ يونٽ ڄاڻائي ٿو.";
D.Urdu["Discovery: The platform identifies potentially compatible, available and eligible donors."]="تلاش: پلیٹ فارم ممکنہ طور پر موزوں، دستیاب اور اہل عطیہ دہندگان کی نشاندہی کرتا ہے۔";D.Sindhi["Discovery: The platform identifies potentially compatible, available and eligible donors."]="ڳولا: پليٽ فارم ممڪن طور مناسب، موجود ۽ اهل عطيو ڏيندڙن جي سڃاڻپ ڪري ٿو.";
D.Urdu["Acceptance: A donor accepts a request. A pending acceptance reserves that donor from accepting another request."]="قبولیت: عطیہ دہندہ درخواست قبول کرتا ہے۔ زیرِ التوا قبولیت کے دوران وہ دوسری درخواست قبول نہیں کر سکتا۔";D.Sindhi["Acceptance: A donor accepts a request. A pending acceptance reserves that donor from accepting another request."]="قبوليت: عطيو ڏيندڙ درخواست قبول ڪري ٿو. انتظار واري قبوليت دوران هو ٻي درخواست قبول نٿو ڪري سگهي.";
D.Urdu["Confirmation: The requester confirms or rejects the proposed match."]="تصدیق: درخواست گزار مجوزہ میچ کی تصدیق یا اسے مسترد کرتا ہے۔";D.Sindhi["Confirmation: The requester confirms or rejects the proposed match."]="تصديق: درخواست ڪندڙ تجويز ڪيل ميچ جي تصديق يا رد ڪري ٿو.";
D.Urdu["A rejected match releases the donor."]="مسترد کیا گیا میچ عطیہ دہندہ کو آزاد کر دیتا ہے۔";D.Sindhi["A rejected match releases the donor."]="رد ٿيل ميچ عطيو ڏيندڙ کي آزاد ڪري ٿو.";
D.Urdu["Communication: Once confirmed, the matched parties can contact each other using Call and WhatsApp actions."]="رابطہ: تصدیق کے بعد دونوں فریق کال اور واٹس ایپ کے ذریعے ایک دوسرے سے رابطہ کر سکتے ہیں۔";D.Sindhi["Communication: Once confirmed, the matched parties can contact each other using Call and WhatsApp actions."]="رابطو: تصديق کان پوءِ ٻئي ڌريون ڪال ۽ واٽس ايپ ذريعي هڪ ٻئي سان رابطو ڪري سگهن ٿيون.";
D.Urdu["Donation: The donor reports the donation and the requester confirms the actual units received."]="عطیہ: عطیہ دہندہ عطیے کی رپورٹ دیتا ہے اور درخواست گزار موصول ہونے والے اصل یونٹس کی تصدیق کرتا ہے۔";D.Sindhi["Donation: The donor reports the donation and the requester confirms the actual units received."]="عطيو: عطيو ڏيندڙ عطئي جي رپورٽ ڏئي ٿو ۽ درخواست ڪندڙ وصول ٿيل اصل يونٽن جي تصديق ڪري ٿو.";
D.Urdu["Completion: Confirmed received units reduce the remaining requirement."]="تکمیل: موصول شدہ تصدیق شدہ یونٹس باقی ضرورت کو کم کرتے ہیں۔";D.Sindhi["Completion: Confirmed received units reduce the remaining requirement."]="مڪمل ٿيڻ: تصديق ٿيل وصول ٿيل يونٽ باقي ضرورت گهٽائين ٿا.";
D.Urdu["Once all requested units are received, the request is marked fulfilled and the donor becomes available for another match."]="تمام مطلوبہ یونٹس موصول ہونے پر درخواست مکمل قرار دی جاتی ہے اور عطیہ دہندہ دوسرے میچ کے لیے دستیاب ہو جاتا ہے۔";D.Sindhi["Once all requested units are received, the request is marked fulfilled and the donor becomes available for another match."]="سڀ گهربل يونٽ ملڻ کان پوءِ درخواست مڪمل قرار ڏني وڃي ٿي ۽ عطيو ڏيندڙ ٻئي ميچ لاءِ موجود ٿي وڃي ٿو.";
D.Urdu["You do not need an account to begin exploring."]="تلاش شروع کرنے کے لیے اکاؤنٹ ضروری نہیں۔";D.Sindhi["You do not need an account to begin exploring."]="ڳولا شروع ڪرڻ لاءِ اڪائونٽ ضروري ناهي.";
D.Urdu["Choose the blood group needed by the patient."]="مریض کے لیے مطلوبہ بلڈ گروپ منتخب کریں۔";D.Sindhi["Choose the blood group needed by the patient."]="مريض لاءِ گهربل رت جو گروپ چونڊيو.";
D.Urdu["The platform will find potentially compatible donor groups."]="پلیٹ فارم ممکنہ طور پر موزوں عطیہ دہندگان کے گروپس دکھائے گا۔";D.Sindhi["The platform will find potentially compatible donor groups."]="پليٽ فارم ممڪن طور مناسب عطيو ڏيندڙن جا گروپ ڏيکاريندو.";
D.Urdu["Explore Compatible Donors and Requests"]="موزوں عطیہ دہندگان اور درخواستیں دیکھیں";D.Sindhi["Explore Compatible Donors and Requests"]="مناسب عطيو ڏيندڙ ۽ درخواستون ڏسو";
D.Urdu["No eligible compatible donors are currently listed."]="اس وقت کوئی اہل اور موزوں عطیہ دہندہ فہرست میں موجود نہیں۔";D.Sindhi["No eligible compatible donors are currently listed."]="هن وقت ڪو اهل ۽ مناسب عطيو ڏيندڙ فهرست ۾ موجود ناهي.";
D.Urdu["Open Blood Requests"]="کھلی خون کی درخواستیں";D.Sindhi["Open Blood Requests"]="کليل رت جون درخواستون";
D.Urdu["Current requests that still need blood donations."]="موجودہ درخواستیں جنہیں ابھی خون کے عطیات درکار ہیں۔";D.Sindhi["Current requests that still need blood donations."]="موجوده درخواستون جن کي اڃا رت جي عطين جي ضرورت آهي.";
D.Urdu["Blood Required · unit(s) remaining · unit(s) requested"]="مطلوبہ خون · باقی یونٹس · درخواست کردہ یونٹس";D.Sindhi["Blood Required · unit(s) remaining · unit(s) requested"]="گهربل رت · باقي يونٽ · درخواست ڪيل يونٽ";
D.Urdu["There are no active blood requests at the moment."]="اس وقت خون کی کوئی فعال درخواست موجود نہیں۔";D.Sindhi["There are no active blood requests at the moment."]="هن وقت رت جي ڪا به فعال درخواست موجود ناهي.";
D.Urdu["Safe and responsible blood donation"]="محفوظ اور ذمہ دارانہ خون کا عطیہ";D.Sindhi["Safe and responsible blood donation"]="محفوظ ۽ ذميواراڻو رت جو عطيو";
D.Urdu["Medical compatibility and eligibility"]="طبی مطابقت اور اہلیت";D.Sindhi["Medical compatibility and eligibility"]="طبي مطابقت ۽ اهليت";
D.Urdu["Blood group compatibility displayed by this platform is intended for preliminary donor discovery only."]="اس پلیٹ فارم پر دکھائی جانے والی بلڈ گروپ مطابقت صرف ابتدائی طور پر عطیہ دہندگان تلاش کرنے کے لیے ہے۔";D.Sindhi["Blood group compatibility displayed by this platform is intended for preliminary donor discovery only."]="هن پليٽ فارم تي ڏيکاريل رت جي گروپ جي مطابقت صرف شروعاتي طور عطيو ڏيندڙ ڳولڻ لاءِ آهي.";
D.Urdu["Actual transfusion suitability must always be determined by qualified medical professionals through appropriate blood-bank testing."]="انتقالِ خون کی حقیقی موزونیت کا تعین ہمیشہ مستند طبی ماہرین کو مناسب بلڈ بینک ٹیسٹ کے ذریعے کرنا چاہیے۔";D.Sindhi["Actual transfusion suitability must always be determined by qualified medical professionals through appropriate blood-bank testing."]="رت چاڙهڻ جي حقيقي موزونيت جو فيصلو هميشه ماهر طبي عملي کي مناسب بلڊ بئنڪ ٽيسٽ ذريعي ڪرڻ گهرجي.";
D.Urdu["Donor health and eligibility must also be assessed by qualified medical staff."]="عطیہ دہندہ کی صحت اور اہلیت کا جائزہ بھی مستند طبی عملے کو لینا چاہیے۔";D.Sindhi["Donor health and eligibility must also be assessed by qualified medical staff."]="عطيو ڏيندڙ جي صحت ۽ اهليت جو جائزو پڻ ماهر طبي عملي کي وٺڻ گهرجي.";
D.Urdu["This platform does not replace medical advice, clinical screening or blood-bank procedures."]="یہ پلیٹ فارم طبی مشورے، طبی جانچ یا بلڈ بینک کے طریقۂ کار کا متبادل نہیں ہے۔";D.Sindhi["This platform does not replace medical advice, clinical screening or blood-bank procedures."]="هي پليٽ فارم طبي صلاح، ڪلينڪل جاچ يا بلڊ بئنڪ جي طريقيڪار جو متبادل ناهي.";
D.Urdu["Create an account to register as a donor, manage your activities, submit emergency requests and participate in donation coordination."]="عطیہ دہندہ کے طور پر رجسٹر ہونے، اپنی سرگرمیاں منظم کرنے، ہنگامی درخواستیں جمع کرانے اور عطیے کی رابطہ کاری میں حصہ لینے کے لیے اکاؤنٹ بنائیں۔";D.Sindhi["Create an account to register as a donor, manage your activities, submit emergency requests and participate in donation coordination."]="عطيو ڏيندڙ طور رجسٽر ٿيڻ، پنهنجون سرگرميون سنڀالڻ، هنگامي درخواستون جمع ڪرائڻ ۽ عطئي جي سهڪار ۾ حصو وٺڻ لاءِ اڪائونٽ ٺاهيو.";
D.Urdu["The platform supports donor registration, blood request matching, secure communication after match confirmation, and donation receipt tracking."]="یہ پلیٹ فارم عطیہ دہندگان کے اندراج، خون کی درخواستوں کی میچنگ، میچ کی تصدیق کے بعد محفوظ رابطے اور عطیے کی وصولی کی نگرانی میں مدد دیتا ہے۔";D.Sindhi["The platform supports donor registration, blood request matching, secure communication after match confirmation, and donation receipt tracking."]="هي پليٽ فارم عطيو ڏيندڙن جي رجسٽريشن، رت جي درخواستن جي ميچنگ، ميچ جي تصديق کان پوءِ محفوظ رابطي ۽ عطئي جي وصولي جي نگراني ۾ مدد ڪري ٿو.";
D.Urdu["Create an account and register your donor profile, or submit a blood request."]="اکاؤنٹ بنائیں اور اپنا عطیہ دہندہ پروفائل رجسٹر کریں، یا خون کی درخواست جمع کرائیں۔";D.Sindhi["Create an account and register your donor profile, or submit a blood request."]="اڪائونٽ ٺاهيو ۽ پنهنجو عطيو ڏيندڙ پروفائل رجسٽر ڪريو، يا رت جي درخواست جمع ڪرايو.";
D.Urdu["The requester reviews and confirms or rejects the proposed match."]="درخواست گزار مجوزہ میچ کا جائزہ لے کر اس کی تصدیق یا اسے مسترد کرتا ہے۔";D.Sindhi["The requester reviews and confirms or rejects the proposed match."]="درخواست ڪندڙ تجويز ڪيل ميچ جو جائزو وٺي ان جي تصديق يا رد ڪري ٿو.";
D.Urdu["After confirmation, the matched parties can coordinate directly."]="تصدیق کے بعد میچ ہونے والے دونوں فریق براہِ راست رابطہ کر سکتے ہیں۔";D.Sindhi["After confirmation, the matched parties can coordinate directly."]="تصديق کان پوءِ ميچ ٿيل ٻئي ڌريون سڌو رابطو ڪري سگهن ٿيون.";
D.Urdu["The donor reports the donation and the requester confirms the units received."]="عطیہ دہندہ عطیے کی رپورٹ دیتا ہے اور درخواست گزار موصولہ یونٹس کی تصدیق کرتا ہے۔";D.Sindhi["The donor reports the donation and the requester confirms the units received."]="عطيو ڏيندڙ عطئي جي رپورٽ ڏئي ٿو ۽ درخواست ڪندڙ وصول ٿيل يونٽن جي تصديق ڪري ٿو.";
D.Urdu["Donor eligibility and health screening rules apply."]="عطیہ دہندہ کی اہلیت اور صحت کی جانچ کے قواعد لاگو ہوتے ہیں۔";D.Sindhi["Donor eligibility and health screening rules apply."]="عطيو ڏيندڙ جي اهليت ۽ صحت جي جاچ جا ضابطا لاڳو ٿين ٿا.";
D.Urdu["The platform does not replace professional medical advice."]="یہ پلیٹ فارم مستند طبی مشورے کا متبادل نہیں ہے۔";D.Sindhi["The platform does not replace professional medical advice."]="هي پليٽ فارم ماهر طبي صلاح جو متبادل ناهي.";
D.Urdu["Create your account to connect with blood donors, respond to emergency requests, and become part of a community working together to help people in need."]="خون کے عطیہ دہندگان سے رابطے، ہنگامی درخواستوں کا جواب دینے اور ضرورت مند افراد کی مدد کے لیے مل کر کام کرنے والی کمیونٹی کا حصہ بننے کے لیے اپنا اکاؤنٹ بنائیں۔";D.Sindhi["Create your account to connect with blood donors, respond to emergency requests, and become part of a community working together to help people in need."]="رت جي عطيو ڏيندڙن سان ڳنڍجڻ، هنگامي درخواستن جو جواب ڏيڻ ۽ ضرورت مند ماڻهن جي مدد لاءِ گڏجي ڪم ڪندڙ ڪميونٽي جو حصو بڻجڻ لاءِ پنهنجو اڪائونٽ ٺاهيو.";
D.Urdu["Join a network that brings donors and people in need together."]="ایسے نیٹ ورک میں شامل ہوں جو عطیہ دہندگان اور ضرورت مند افراد کو جوڑتا ہے۔";D.Sindhi["Join a network that brings donors and people in need together."]="اهڙي نيٽ ورڪ ۾ شامل ٿيو جيڪو عطيو ڏيندڙن ۽ ضرورت مند ماڻهن کي گڏ ڪري ٿو.";
D.Urdu["Already have an account?"]="کیا آپ کا پہلے سے اکاؤنٹ موجود ہے؟";D.Sindhi["Already have an account?"]="ڇا توهان وٽ اڳ ۾ اڪائونٽ آهي؟";
D.Urdu["Your CNIC and account credentials are private."]="آپ کا CNIC اور اکاؤنٹ کی معلومات نجی ہیں۔";D.Sindhi["Your CNIC and account credentials are private."]="توهان جو CNIC ۽ اڪائونٽ جا تفصيل ذاتي آهن.";
D.Urdu["Every drop can make a difference."]="خون کا ہر قطرہ فرق پیدا کر سکتا ہے۔";D.Sindhi["Every drop can make a difference."]="رت جو هر قطرو فرق آڻي سگهي ٿو.";
D.Urdu["Blood Donor Network | Connecting donors with people in need. Every donation brings hope."]="بلڈ ڈونر نیٹ ورک | عطیہ دہندگان کو ضرورت مند افراد سے جوڑنا۔ ہر عطیہ امید پیدا کرتا ہے۔";D.Sindhi["Blood Donor Network | Connecting donors with people in need. Every donation brings hope."]="رت جو عطيو ڏيندڙ نيٽ ورڪ | عطيو ڏيندڙن کي ضرورت مند ماڻهن سان ڳنڍڻ. هر عطيو اميد پيدا ڪري ٿو.";
D.Urdu["Blood Donor Network | Connecting donors with people in need."]="بلڈ ڈونر نیٹ ورک | عطیہ دہندگان کو ضرورت مند افراد سے جوڑنا۔";D.Sindhi["Blood Donor Network | Connecting donors with people in need."]="رت جو عطيو ڏيندڙ نيٽ ورڪ | عطيو ڏيندڙن کي ضرورت مند ماڻهن سان ڳنڍڻ.";
D.Urdu["Every donation brings hope."]="ہر عطیہ امید پیدا کرتا ہے۔";D.Sindhi["Every donation brings hope."]="هر عطيو اميد پيدا ڪري ٿو.";
D.Urdu["Your willingness to donate may help someone in an emergency."]="آپ کا خون عطیہ کرنے کا ارادہ کسی ہنگامی صورتحال میں کسی کی مدد کر سکتا ہے۔";D.Sindhi["Your willingness to donate may help someone in an emergency."]="توهان جي رت عطيو ڪرڻ جي خواهش هنگامي حالت ۾ ڪنهن جي مدد ڪري سگهي ٿي.";
D.Urdu["Register your details so people searching for a matching blood group can find a potential donor."]="اپنی تفصیلات درج کریں تاکہ موزوں بلڈ گروپ تلاش کرنے والے افراد ممکنہ عطیہ دہندہ تلاش کر سکیں۔";D.Sindhi["Register your details so people searching for a matching blood group can find a potential donor."]="پنهنجا تفصيل داخل ڪريو ته جيئن مناسب رت جو گروپ ڳوليندڙ ماڻهو ممڪن عطيو ڏيندڙ ڳولي سگهن.";
D.Urdu["Enter accurate information. Fields marked with"]="درست معلومات درج کریں۔ جن خانوں پر";D.Sindhi["Enter accurate information. Fields marked with"]="صحيح معلومات داخل ڪريو. جن خانن تي";
D.Urdu["are required."]="لازمی ہیں۔";D.Sindhi["are required."]="اهي لازمي آهن.";
D.Urdu["Answer all five questions honestly. These answers are for preliminary screening only and do not determine medical eligibility."]="پانچوں سوالات کے جواب دیانت داری سے دیں۔ یہ جوابات صرف ابتدائی جانچ کے لیے ہیں اور طبی اہلیت کا حتمی فیصلہ نہیں کرتے۔";D.Sindhi["Answer all five questions honestly. These answers are for preliminary screening only and do not determine medical eligibility."]="پنجن ئي سوالن جا جواب ايمانداري سان ڏيو. اهي جواب صرف شروعاتي جاچ لاءِ آهن ۽ طبي اهليت جو آخري فيصلو نٿا ڪن.";
D.Urdu["No, this is my first time"]="نہیں، یہ میرا پہلا عطیہ ہے";D.Sindhi["No, this is my first time"]="نه، هي منهنجو پهريون عطيو آهي";
D.Urdu["Yes, I have donated before"]="جی ہاں، میں پہلے خون عطیہ کر چکا ہوں";D.Sindhi["Yes, I have donated before"]="ها، مون اڳ ۾ رت عطيو ڪيو آهي";
D.Urdu["Enter the date of your most recent donation. The date cannot be in the future."]="اپنے حالیہ ترین خون کے عطیے کی تاریخ درج کریں۔ یہ تاریخ مستقبل کی نہیں ہو سکتی۔";D.Sindhi["Enter the date of your most recent donation. The date cannot be in the future."]="پنهنجي تازي رت جي عطئي جي تاريخ داخل ڪريو. اها تاريخ مستقبل جي نه ٿي سگهي.";
D.Urdu["A qualified healthcare professional must make the final decision about whether you can donate."]="آپ خون عطیہ کر سکتے ہیں یا نہیں، اس کا حتمی فیصلہ مستند طبی ماہر کو کرنا چاہیے۔";D.Sindhi["A qualified healthcare professional must make the final decision about whether you can donate."]="توهان رت عطيو ڪري سگهو ٿا يا نه، ان جو آخري فيصلو ماهر طبي عملي کي ڪرڻ گهرجي.";
D.Urdu["Select your blood group carefully. Medical professionals must confirm blood compatibility before transfusion."]="اپنا بلڈ گروپ احتیاط سے منتخب کریں۔ انتقالِ خون سے پہلے طبی ماہرین کو مطابقت کی تصدیق کرنی چاہیے۔";D.Sindhi["Select your blood group carefully. Medical professionals must confirm blood compatibility before transfusion."]="پنهنجو رت جو گروپ احتياط سان چونڊيو. رت چاڙهڻ کان اڳ طبي عملي کي مطابقت جي تصديق ڪرڻ گهرجي.";
D.Urdu["Provide your city or area so potential recipients can identify donors in a suitable location."]="اپنا شہر یا علاقہ درج کریں تاکہ ممکنہ وصول کنندگان مناسب مقام پر عطیہ دہندگان تلاش کر سکیں۔";D.Sindhi["Provide your city or area so potential recipients can identify donors in a suitable location."]="پنهنجو شهر يا علائقو ڏيو ته جيئن ممڪن وصول ڪندڙ مناسب هنڌ تي عطيو ڏيندڙ ڳولي سگهن.";
D.Urdu["The system uses your last donation date to apply its minimum 90-day interval rule."]="سسٹم آپ کے آخری عطیے کی تاریخ کے مطابق کم از کم 90 دن کے وقفے کا اصول لاگو کرتا ہے۔";D.Sindhi["The system uses your last donation date to apply its minimum 90-day interval rule."]="سسٽم توهان جي آخري عطئي جي تاريخ موجب گهٽ ۾ گهٽ 90 ڏينهن جي وقفي جو اصول لاڳو ڪري ٿو.";
D.Urdu["Health answers should be restricted to authorised handling and never shown in public donor search results."]="صحت سے متعلق جوابات تک رسائی صرف مجاز افراد تک محدود ہونی چاہیے اور انہیں عوامی عطیہ دہندہ تلاش کے نتائج میں کبھی نہیں دکھانا چاہیے۔";D.Sindhi["Health answers should be restricted to authorised handling and never shown in public donor search results."]="صحت بابت جوابن تائين رسائي صرف اجازت يافته ماڻهن تائين محدود هجڻ گهرجي ۽ اهي عوامي عطيو ڏيندڙ ڳولا جي نتيجن ۾ ڪڏهن به نه ڏيکاريا وڃن.";
D.Urdu["Important: Registration does not mean you are medically approved to donate."]="اہم: رجسٹریشن کا مطلب یہ نہیں کہ آپ کو طبی طور پر خون عطیہ کرنے کی منظوری مل گئی ہے۔";D.Sindhi["Important: Registration does not mean you are medically approved to donate."]="اهم: رجسٽريشن جو مطلب اهو ناهي ته توهان کي طبي طور رت عطيو ڪرڻ جي منظوري ملي وئي آهي.";
D.Urdu["The system's 90-day rule is an administrative screening rule, not a complete medical eligibility assessment."]="سسٹم کا 90 دن کا اصول انتظامی ابتدائی جانچ ہے، مکمل طبی اہلیت کا جائزہ نہیں۔";D.Sindhi["The system's 90-day rule is an administrative screening rule, not a complete medical eligibility assessment."]="سسٽم جو 90 ڏينهن وارو اصول انتظامي شروعاتي جاچ آهي، مڪمل طبي اهليت جو جائزو ناهي.";
for (const [key, urdu, sindhi] of EXTRA) {
  D.Urdu[key] = urdu;
  D.Sindhi[key] = sindhi;
}
const dict=D[lang],keys=Object.keys(dict).sort((a,b)=>b.length-a.length);
function tr(s){if(!s.trim())return s;const lead=(s.match(/^\s*/) || [""])[0];const tail=(s.match(/\s*$/) || [""])[0];let body=s.trim().replace(/\s+/g," ");for(const k of keys)body=body.split(k).join(dict[k]);return lead+body+tail;}
function scan(root){
const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),a=[];
while(w.nextNode())a.push(w.currentNode);
a.forEach(n=>{if(n.parentElement&&!n.parentElement.closest("script,style,noscript,textarea,code,pre,h1,.brand strong,[data-no-translate]"))n.nodeValue=tr(n.nodeValue);});
root.querySelectorAll("[placeholder],[aria-label],[alt],[title]").forEach(e=>{if(e.closest("h1,.brand strong,[data-no-translate]"))return;["placeholder","aria-label","alt","title"].forEach(k=>{if(e.hasAttribute(k))e.setAttribute(k,tr(e.getAttribute(k)));});});
root.querySelectorAll('input[type="submit"],input[type="button"],input[type="reset"]').forEach(e=>{e.value=tr(e.value);});
}
document.documentElement.lang=lang==="Urdu"?"ur":"sd";document.documentElement.dir="rtl";
const style=document.createElement("style");style.textContent='html[dir="rtl"] body{direction:rtl;font-family:Tahoma,Arial,sans-serif}html[dir="rtl"] input,html[dir="rtl"] textarea,html[dir="rtl"] select{text-align:right}html[dir="rtl"] .dashboard-header,html[dir="rtl"] .header,html[dir="rtl"] .page-header,html[dir="rtl"] .desktop-nav,html[dir="rtl"] .nav,html[dir="rtl"] .brand,html[dir="rtl"] .notification-card{direction:rtl}html[dir="rtl"] input[type="tel"],html[dir="rtl"] input[type="email"],html[dir="rtl"] input[type="date"],html[dir="rtl"] input[type="number"]{direction:ltr;text-align:left}';document.head.appendChild(style);
function start(){scan(document.body);}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start,{once:true});else start();
new MutationObserver(rs=>rs.forEach(r=>r.addedNodes.forEach(n=>{if(n.nodeType===3&&n.parentElement&&!n.parentElement.closest("script,style,noscript,textarea,code,pre,h1,.brand strong,[data-no-translate]"))n.nodeValue=tr(n.nodeValue);else if(n.nodeType===1)scan(n);}))).observe(document.documentElement,{childList:true,subtree:true});
})();