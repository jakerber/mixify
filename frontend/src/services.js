const API_URL_BASE = process.env.REACT_APP_API_URL;

const execRequest = async (url) => {
    return fetch(url)
        .then(response => response.json())
        .then(response => {
            if (!response.hasOwnProperty('error_message')) return response;
            throw Error(JSON.stringify(response, null, ' '));
        })
        .catch(error => {
            throw Error(error);
        });
}

export const QUEUE_NOT_FOUND_ERROR_MSG = 'queue not found';

export const fetchQueue = async (queueName, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/${queueName}/${fpjsVisitorId}`);
};

export const createQueue = async (spotifyAccessToken, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/new/${spotifyAccessToken}/${fpjsVisitorId}`);
};

export const upvoteSong = async (queueTrackId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/upvote/${queueTrackId}/${fpjsVisitorId}`);
};

export const removeSongUpvote = async (queueTrackId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/upvote/remove/${queueTrackId}/${fpjsVisitorId}`);
};

export const searchForSong = async (queueId, searchQuery) => {
    return execRequest(`${API_URL_BASE}/v1/search/${queueId}/${searchQuery}`);
};

export const addSongToQueue = async (queueId, spotifyTrackId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/add/${queueId}/${spotifyTrackId}/${fpjsVisitorId}`);
};

export const endQueue = async (queueId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/end/${queueId}/${fpjsVisitorId}`);
};

export const pauseQueue = async (queueId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/pause/${queueId}/${fpjsVisitorId}`);
};

export const unpauseQueue = async (queueId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/unpause/${queueId}/${fpjsVisitorId}`);
};

export const subscribeToQueue = async (queueId, spotifyAccessToken, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/subscribe/${queueId}/${spotifyAccessToken}/${fpjsVisitorId}`);
};

export const unsubscribeFromQueue = async (queueId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/unsubscribe/${queueId}/${fpjsVisitorId}`);
};

export const boostQueueSong = async (queueSongId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/boost/${queueSongId}/${fpjsVisitorId}`);
};

export const createBoostPayment = async (queueSongId, fpjsVisitorId) => {
    return execRequest(`${API_URL_BASE}/v1/queue/boost/payment/${queueSongId}/${fpjsVisitorId}`);
};