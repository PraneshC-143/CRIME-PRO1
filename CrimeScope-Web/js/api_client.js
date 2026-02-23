/**
 * API Client for interacting with the Python Flask Backend
 */

const API_BASE_URL = 'http://127.0.0.com/api'; // Ensure your Flask app runs on this port. We use 127.0.0.1 for local dev.
// Note: Changed to 127.0.0.1:5000 based on standard Flask config.
const API_URL = 'http://127.0.0.1:5000/api';

const ApiClient = {
    /**
     * Fetch high-level statistics (Total Crimes, YoY Growth, Top State)
     */
    async getStats(state = 'all', minYear = 2017, maxYear = 2023) {
        try {
            const response = await fetch(`${API_URL}/stats?state=${encodeURIComponent(state)}&min_year=${minYear}&max_year=${maxYear}`);
            if (!response.ok) throw new Error('API Error fetching stats');
            return await response.json();
        } catch (error) {
            console.error(error);
            return null;
        }
    },

    /**
     * Fetch trend line chart data (Yearly totals)
     */
    async getTrend(state = 'all') {
        try {
            const response = await fetch(`${API_URL}/chart/trend?state=${encodeURIComponent(state)}`);
            if (!response.ok) throw new Error('API Error fetching trend data');
            return await response.json();
        } catch (error) {
            console.error(error);
            return null;
        }
    },

    /**
     * Fetch the machine learning prediction for a target year
     */
    async getPrediction(state = 'all', targetYear = 2024) {
        try {
            const response = await fetch(`${API_URL}/predict?state=${encodeURIComponent(state)}&target_year=${targetYear}`);
            if (!response.ok) throw new Error('API Error fetching prediction');
            return await response.json();
        } catch (error) {
            console.error(error);
            return null;
        }
    }
};

window.ApiClient = ApiClient;
