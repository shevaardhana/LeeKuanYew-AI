import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Pre-defined high-quality seed data covering core themes (Survival, Leadership, Geopolitics, Nation Building)
SEED_DATA = [
    # ------------------ THEME: SURVIVAL & INDEPENDENCE ------------------
    {
        "text": """On 9 August 1965, Lee Kuan Yew announced the separation of Singapore from Malaysia, marking the birth of an independent but highly vulnerable city-state. 
In his historic televised press conference, he spoke with raw emotion: 'For me, it is a moment of anguish. All my life, my whole adult life, I have believed in merger and unity of the two territories. We are connected by geography, economy, and ties of kinship.' 
He reassured the citizens of the new nation: 'We are going to be a multi-racial nation. We will set the example. This is not a Malay nation; this is not a Chinese nation; this is not an Indian nation. Everyone will have his place, equal language, equal opportunity, equal religion. We will survive. Ten years from now, this will be a bustling metropolis.' 
This moment defined Singapore's survivalist mindset—the absolute necessity of self-reliance, unity, and excellence to overcome the lack of land, natural resources, and military defense.""",
        "metadata": {"source": "1965 Separation Press Conference", "theme": "Survival"}
    },
    {
        "text": """Water security was the ultimate vulnerability for Singapore after separation. Under the 1961 and 1962 Water Agreements with Johor (Malaysia), Singapore was dependent on Malaysia for its daily water supply. Lee Kuan Yew famously remarked that water was a matter of life and death, and that if water supply was cut off, it would be an act of war. 
To ensure survival, Lee spearheaded the 'Four National Taps' strategy: local catchment water, imported water from Malaysia, reclaimed water (NEWater), and desalinated water. Through decades of heavy investment in technology and reservoir creation, Singapore turned its vulnerability into a strategic asset, achieving high levels of water self-sufficiency.""",
        "metadata": {"source": "Memoirs / Water Security Strategy", "theme": "Survival"}
    },
    {
        "text": """Building the Singapore Armed Forces (SAF) from scratch was a monumental task for the infant republic. In 1965, Singapore had only two infantry regiments, led mostly by British and Malaysian officers. 
Lee Kuan Yew knew that without a credible defense, Singapore's sovereignty was an illusion. 'Without an army, we are defenseless. Anyone can bully us. We had to build an army, and we had to do it fast.' 
He sought help from various nations. While others hesitated, Israel stepped up secretly, sending military advisors (codenamed 'Mexicans') to train the first batches of SAF officers. Lee introduced National Service (NS) in 1967, mandating military service for all young male citizens. This not only built a formidable deterrent force but also served as a critical crucible for social integration and nation-building.""",
        "metadata": {"source": "The Singapore Story / SAF History", "theme": "Survival"}
    },

    # ------------------ THEME: LEADERSHIP & GOVERNANCE ------------------
    {
        "text": """Lee Kuan Yew's philosophy on political power and leadership was uncompromising and pragmatic. In a rally speech in 1980, he declared:
'Whoever governs Singapore must have that iron in him. Or give it up. This is not a game of cards. This is your life and mine. I've spent a whole lifetime building this and as long as I'm in charge, nobody is going to knock it down.'
He believed that governing Singapore required extreme resilience, foresight, and the willingness to make highly unpopular but necessary long-term decisions. For Lee, a leader's job was not to seek popularity, but to do what was right for the country's survival and prosperity.""",
        "metadata": {"source": "1980 National Day Rally Speech", "theme": "Leadership"}
    },
    {
        "text": """Integrity and the eradication of corruption were the foundation of Lee Kuan Yew's administration. When the People's Action Party (PAP) took power in 1959, they wore all-white uniforms to symbolize purity and honesty. 
Lee established a strict anti-corruption framework, empowering the Corrupt Practices Investigation Bureau (CPIB) to investigate anyone, regardless of status. He paid ministers high salaries linked to private-sector benchmarks to reduce the temptation of bribery and attract top-tier talent. 'If you pay peanuts, you get monkeys,' he argued. This zero-tolerance policy created a clean, transparent business environment that attracted global multinational corporations.""",
        "metadata": {"source": "From Third World to First / Anti-Corruption Policy", "theme": "Leadership"}
    },
    {
        "text": """Lee Kuan Yew was famously tough on political opponents and critics. He believed that Singapore was too small and fragile to tolerate disruptive, demagogic politics. 
He once said: 'Anybody who decides to take me on needs to put on knuckle-dusters. If you think you can hurt me more than I can hurt you, try. There is no other way you can govern a Chinese-majority, multi-racial society in Southeast Asia.' 
He used defamation lawsuits to defend his reputation and maintain political stability, arguing that if a leader's integrity is compromised, their moral authority to govern is destroyed.""",
        "metadata": {"source": "Speech at National Day Rally", "theme": "Leadership"}
    },

    # ------------------ THEME: GEOPOLITICS & FOREIGN POLICY ------------------
    {
        "text": """Singapore's foreign policy is rooted in pragmatism, realism, and balance. As a small state, Singapore cannot afford to make enemies or take dogmatic ideological stances. Lee Kuan Yew formulated a foreign policy aimed at making Singapore 'a relevant nation' to the global superpowers. 
He stated: 'A small state must make itself relevant to the world. If we are not relevant, we will cease to exist.' 
He focused on maintaining excellent relations with both the United States and China, serving as a trusted interlocutor and geopolitical analyst for leaders of both superpowers. By keeping Singapore open, stable, and strategically useful, he ensured its safety and economic survival.""",
        "metadata": {"source": "From Third World to First / Geopolitical Strategy", "theme": "Geopolitics"}
    },
    {
        "text": """Lee Kuan Yew was one of the world's most respected observers of China's rise. He maintained close relationships with Chinese leaders, starting with Deng Xiaoping in 1978. Deng visited Singapore and was inspired by its combination of economic freedom and political discipline, which heavily influenced China's 'Open Door' reforms. 
Lee predicted early on that China would become a formidable global power: 'The size of China's displacement of the world balance is such that the world must find a new balance. It is not possible to pretend that this is just another big player. This is the biggest player in the history of man.' 
He advised Western nations to engage and integrate China into the global system rather than trying to contain it, while simultaneously advising China to grow peacefully.""",
        "metadata": {"source": "Interviews and Speeches on China", "theme": "Geopolitics"}
    },
    {
        "text": """Lee Kuan Yew believed that regional stability in Southeast Asia was vital for Singapore's economic progress. He played a key role in the formation of ASEAN (Association of Southeast Asian Nations) in 1967. 
Despite initial tensions and historical conflicts between member countries (such as Indonesia's Konfrontasi against Malaysia/Singapore), Lee worked to foster cooperation and trust. ASEAN provided a collective voice for Southeast Asia during the Cold War and created a peaceful regional environment that allowed Singapore to focus on industrialization and global trade.""",
        "metadata": {"source": "ASEAN Foundations", "theme": "Geopolitics"}
    },

    # ------------------ THEME: NATION BUILDING & DEVELOPMENT ------------------
    {
        "text": """The Housing and Development Board (HDB) flat ownership scheme was a cornerstone of Lee Kuan Yew's nation-building strategy. In 1960, most Singaporeans lived in squalid, overcrowded slums. 
Lee wanted citizens to own their homes: 'I believed that if every family owned its own home, the country would be much more stable. Homeownership gives a man a sense of ownership, a stake in the nation's future. He will fight to defend it.' 
By providing affordable public housing and allowing citizens to use their Central Provident Fund (CPF) savings to pay for mortgages, Lee transformed Singapore into a nation of homeowners, fostering social cohesion and national identity across different races.""",
        "metadata": {"source": "The Singapore Story / Housing Reform", "theme": "Nation Building"}
    },
    {
        "text": """To attract foreign investments, Lee Kuan Yew wanted to make Singapore stand out visually and culturally. He initiated the 'Keep Singapore Clean and Green' campaign in 1968, transforming Singapore into a 'Garden City'. 
He explained: 'After independence, I searched for some way to distinguish ourselves from other developing countries. I settled on a clean and green Singapore. If we are clean, green, and efficient, it shows we are disciplined, organized, and a safe place for investment. It was the most cost-effective project we ever launched.' 
Lee personally checked on the progress of tree planting along highways and the cleaning of rivers, making environmental care a national discipline.""",
        "metadata": {"source": "Garden City Speech / Memoirs", "theme": "Nation Building"}
    },
    {
        "text": """Bilingualism was a critical and highly contested policy implemented by Lee Kuan Yew's government. Lee established English as the primary language of instruction and administration, ensuring Singaporeans could connect to the global economy and access international science and technology. 
At the same time, students were required to learn their mother tongue (Mandarin, Malay, or Tamil) as a second language to preserve their cultural heritage, values, and identity. 
'English is our working language. It gives us access to the world. The mother tongue gives us our values, our self-confidence, and our roots.' 
This pragmatic compromise bridged ethnic divides and gave Singapore a unique global advantage.""",
        "metadata": {"source": "Bilingualism Policy Address", "theme": "Nation Building"}
    },
    {
        "text": """Education and meritocracy were the twin engines of Singapore's social mobility and economic growth. Lee Kuan Yew believed that in a nation with no natural resources, the only resource is human talent. 'Our job was to build a system where the best rise to the top, regardless of race, class, parentage, or wealth. We invested heavily in education, making bilingual school systems and teaching practical sciences.' Lee insisted on rewarding talent through merit-based scholarships and public service recruitment, ensuring that the country's administration was led by its most brilliant minds rather than political connections.""",
        "metadata": {"source": "From Third World to First / Education Strategy", "theme": "Nation Building"}
    },
    {
        "text": """To leapfrog hostile neighbors and lack of resources, Lee Kuan Yew designed a unique economic strategy: skip the region and connect directly with developed economies like the United States, Europe, and Japan. By inviting multinational corporations (MNCs) to set up manufacturing hubs in Singapore, Lee created thousands of jobs. Critics warned that MNCs would exploit Singapore, but Lee argued: 'We had to plug into the global grid. MNCs brought technology, management, and global markets. They helped us bridge the gap between third world and first world status in a single generation.'""",
        "metadata": {"source": "The Singapore Story / Global Market Integration", "theme": "Geopolitics"}
    },
    {
        "text": """Lee Kuan Yew defended Singapore's strict legal system and high levels of discipline as essential to its survival. 'In a small, vulnerable island state, you cannot afford disorder. Without law and order, there is no investment. Without investment, there are no jobs.' Lee implemented tough penalties, including corporal punishment (caning) and capital punishment, to deter crime. He believed that the primary duty of government is to provide a safe, secure, and predictable environment for its citizens, arguing that individual liberties must sometimes yield to the collective security of the nation.""",
        "metadata": {"source": "Parliamentary Debate / Law and Order", "theme": "Leadership"}
    },
    {
        "text": """Racial harmony was not just a moral goal for Lee Kuan Yew; it was a security imperative. Having witnessed the bloody race riots of 1964, Lee was determined to prevent communal conflicts from tearing Singapore apart. He enacted the Internal Security Act (ISA) to detain extremists before they could incite violence, and established the Presidential Council for Minority Rights to ensure no legislation discriminated against minority groups. Lee famously noted: 'We are not a homogeneous society. We must construct a system of checks and balances where every community feels secure and valued.'""",
        "metadata": {"source": "Reflections on 1964 Riots / National Security", "theme": "Survival"}
    },
    {
        "text": """Lee Kuan Yew's governing style was defined by pragmatism rather than political ideology. He rejected both raw capitalism and pure socialism. 'Does it work? If it works, let's try it. If it doesn't work, we throw it out and try something else.' He used this approach to guide key policies, such as establishing government-linked corporations (like Singapore Airlines and Temasek Holdings) to drive key economic sectors while keeping them run on strict private-sector, profit-driven lines without government subsidies.""",
        "metadata": {"source": "Interview on Pragmatic Socialism", "theme": "Leadership"}
    },
    {
        "text": """Lee Kuan Yew held a distinct view on the role of the media in a developing nation. He rejected the Western model of an adversarial press. 'In Singapore, the press must help the government explain policies to the people, and foster national cohesion. We cannot allow foreign-owned or foreign-funded media to set the agenda or stir up racial tensions in our society.' He implemented licensing laws for newspapers, ensuring that the media worked as a partner in nation-building rather than a destructive political force.""",
        "metadata": {"source": "Address to the International Press Institute", "theme": "Leadership"}
    }
]

# Scrape quotes from Wikiquote
def scrape_wikiquote():
    url = "https://en.wikiquote.org/wiki/Lee_Kuan_Yew"
    quotes = []
    print("Scraping quotes from Wikiquote...")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find(class_="mw-parser-output")
            if content:
                current_section = "include"
                for child in content.children:
                    if child.name in ["h2", "h3"]:
                        span = child.find(class_="mw-headline")
                        if span:
                            headline_id = span.get("id", "").lower()
                            # Exclude sections containing quotes ABOUT him or references
                            if any(x in headline_id for x in ["about", "references", "external", "see_also"]):
                                current_section = "exclude"
                            else:
                                current_section = "include"
                    elif child.name == "ul" and current_section == "include":
                        for li in child.find_all("li", recursive=False):
                            text = li.get_text().strip()
                            # Clean up and filter
                            if len(text) > 40 and not text.startswith("^") and "citation needed" not in text.lower():
                                # Remove reference brackets (e.g. [1], [23])
                                text = re.sub(r'\[\d+\]', '', text)
                                quotes.append(text)
            print(f"Scraped {len(quotes)} quotes successfully.")
        else:
            print(f"Failed to fetch Wikiquote. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error scraping Wikiquote: {e}")
    return quotes

def build_index():
    print("Building FAISS index...")
    # Initialize list of LangChain documents
    documents = []

    # Add seed data
    for item in SEED_DATA:
        doc = Document(page_content=item["text"], metadata=item["metadata"])
        documents.append(doc)

    # Scrape Wikiquote quotes
    scraped_quotes = scrape_wikiquote()
    for q in scraped_quotes:
        # Check if quote is too long, we might want to tag them
        doc = Document(
            page_content=q,
            metadata={"source": "Wikiquote", "theme": "General Quotes"}
        )
        documents.append(doc)

    if not documents:
        print("Error: No documents collected. Exiting.")
        sys.exit(1)

    print(f"Total documents collected (Seeds + Scraped): {len(documents)}")

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} text chunks.")

    # Create HuggingFace embeddings
    print("Generating embeddings using local HuggingFace all-MiniLM-L6-v2 model...")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Build FAISS vector store
    db = FAISS.from_documents(split_docs, embeddings)
    
    # Save locally
    index_path = "faiss_index"
    db.save_local(index_path)
    print(f"FAISS index built and saved successfully to '{index_path}/'.")

if __name__ == "__main__":
    build_index()
