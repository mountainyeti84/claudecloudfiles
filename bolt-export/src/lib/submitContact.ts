// Sends a form to the same Supabase function the "Let's Chat" wizard uses
// (supabase/functions/submit-contact-form), so it lands in contact_submissions
// and emails andy@adsyeti.com.
export interface ContactPayload {
  name: string;
  email: string;
  company?: string;
  monthlySpend?: string;
  primaryChallenge: string;
  message: string;
}

export async function submitContact(p: ContactPayload) {
  const url = import.meta.env.VITE_SUPABASE_URL || '';
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
  const res = await fetch(`${url}/functions/v1/submit-contact-form`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({ company: '', monthlySpend: '', ...p }),
  });
  if (!res.ok) throw new Error('bad status ' + res.status);
}
