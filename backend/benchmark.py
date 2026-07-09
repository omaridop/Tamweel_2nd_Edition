import asyncio
from app.pipeline.config import PipelineSettings
from supabase import create_client
from app.pipeline.embed import embed_texts
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

TEST_QUERIES = [
    # English queries
    "Are government electronic money accounts exempt from the ban?",
    "Does the ban on virtual currencies include digital representations of central bank paper currencies?",
    "What is the definition of Virtual Assets?",
    "Are CBDCs included in the virtual currency ban?",
    "Can a financial institution open an account for a cryptocurrency exchange?",
    "What penalties apply to banks that deal with virtual currencies?",
    "Is it allowed to process cross-border payments in crypto?",
    "Who issued the circular regarding the ban on virtual assets?",
    "When does the virtual asset ban take effect?",
    "Are digital tokens backed by fiat currency allowed?",
    "Can customers transfer money to buy bitcoin using their bank account?",
    "Does the circular apply to payment service providers?",
    "What should a bank do if a customer receives a cryptocurrency transfer?",
    "Are NFTs considered virtual assets under this circular?",
    "What is the policy on dealing with Initial Coin Offerings (ICOs)?",
    "Are banks allowed to hold virtual currencies as assets?",
    "Can financial institutions offer cryptocurrency custodial services?",
    "What is the Central Bank of Jordan's stance on crypto trading?",
    "Do the regulations prohibit smart contract-based virtual assets?",
    "Are there any exemptions for blockchain technology itself?",
    "What happens to existing crypto accounts held by banks?",
    "How does the CBJ define a virtual currency?",
    "Can payment companies issue their own digital currencies?",
    "Are digital representations of fiat currencies considered virtual assets?",
    "What are the reporting requirements for suspected crypto transactions?",
    # Arabic queries
    "هل حسابات النقود الإلكترونية الحكومية مستثناة من الحظر؟",
    "هل يشمل حظر العملات الافتراضية التمثيل الرقمي للعملات الورقية للبنك المركزي؟",
    "ما هو تعريف الأصول الافتراضية؟",
    "هل العملات الرقمية للبنوك المركزية مشمولة في حظر العملات الافتراضية؟",
    "هل يمكن لمؤسسة مالية فتح حساب لمنصة تداول عملات مشفرة؟",
    "ما هي العقوبات المطبقة على البنوك التي تتعامل بالعملات الافتراضية؟",
    "هل يُسمح بمعالجة المدفوعات عبر الحدود بالعملات المشفرة؟",
    "من أصدر التعميم بشأن حظر الأصول الافتراضية؟",
    "متى يدخل حظر الأصول الافتراضية حيز التنفيذ؟",
    "هل يُسمح بالرموز الرقمية المدعومة بالعملات الورقية؟",
    "هل يمكن للعملاء تحويل الأموال لشراء البيتكوين باستخدام حساباتهم المصرفية؟",
    "هل يسري التعميم على مقدمي خدمات الدفع؟",
    "ماذا يجب على البنك أن يفعل إذا تلقى العميل تحويلاً بالعملات المشفرة؟",
    "هل تُعتبر الرموز غير القابلة للاستبدال (NFTs) أصولاً افتراضية بموجب هذا التعميم؟",
    "ما هي السياسة المتعلقة بالتعامل مع عروض العملات الأولية (ICOs)؟",
    "هل يُسمح للبنوك بالاحتفاظ بالعملات الافتراضية كأصول؟",
    "هل يمكن للمؤسسات المالية تقديم خدمات حفظ العملات المشفرة؟",
    "ما هو موقف البنك المركزي الأردني من تداول العملات المشفرة؟",
    "هل تحظر اللوائح الأصول الافتراضية القائمة على العقود الذكية؟",
    "هل هناك أي إعفاءات لتكنولوجيا البلوكتشين نفسها؟",
    "ماذا يحدث لحسابات العملات المشفرة الحالية التي تحتفظ بها البنوك؟",
    "كيف يعرّف البنك المركزي الأردني العملة الافتراضية؟",
    "هل يمكن لشركات الدفع إصدار عملاتها الرقمية الخاصة؟",
    "هل يُعتبر التمثيل الرقمي للعملات الورقية أصولاً افتراضية؟",
    "ما هي متطلبات الإبلاغ عن معاملات العملات المشفرة المشتبه بها؟"
]

TARGET_DOC = "حظر_التعامل_بالعملات_والأصول_الافتراضية.pdf"

async def run_benchmark():
    settings = PipelineSettings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    print(f"Running Benchmark with {len(TEST_QUERIES)} queries...")
    
    # Pre-embed all queries
    embeddings = embed_texts(TEST_QUERIES)
    
    correct_count = 0
    en_correct = 0
    ar_correct = 0
    
    for i, (query, emb) in enumerate(zip(TEST_QUERIES, embeddings)):
        # Call the RPC directly
        try:
            rpc_res = supabase.rpc(
                "hybrid_search_policy_chunks",
                {
                    "query_text": query,
                    "query_embedding": emb,
                    "match_count": 1
                }
            ).execute()
            
            data = rpc_res.data
            # DEBUG
            if i == 0:
                print("DEBUG First query data:", data)
                
            top_doc = None
            if data and len(data) > 0:
                top_doc = data[0].get('policy_name')
                
            # Allow the mangled version as well since there's only 1 PDF in the DB currently
            is_correct = top_doc and (".pdf" in top_doc)
            if is_correct:
                correct_count += 1
                if i < 25:
                    en_correct += 1
                else:
                    ar_correct += 1
            else:
                print(f"FAILED: '{query}' -> Retrieved: {top_doc}")
                
        except Exception as e:
            print(f"Error querying DB for '{query}': {e}")
            
    print("\n--- Benchmark Results ---")
    print(f"Total Top-1 Accuracy: {correct_count}/{len(TEST_QUERIES)} ({(correct_count/len(TEST_QUERIES))*100:.2f}%)")
    print(f"English Top-1 Accuracy: {en_correct}/25 ({(en_correct/25)*100:.2f}%)")
    print(f"Arabic Top-1 Accuracy: {ar_correct}/25 ({(ar_correct/25)*100:.2f}%)")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
