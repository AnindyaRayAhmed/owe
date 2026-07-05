const API_BASE = '/api';

export const fetchBrief = async () => {
  const response = await fetch(`${API_BASE}/brief`);
  if (!response.ok) throw new Error('Failed to fetch brief');
  return response.json();
};

export const fetchMissions = async () => {
  const response = await fetch(`${API_BASE}/missions`);
  if (!response.ok) throw new Error('Failed to fetch missions');
  return response.json();
};

export const sendChatMessage = async (message) => {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
};
