import { useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { subscribeToQueue } from '../services';
import { Paper, Center, Stack, Text, Loader } from '@mantine/core';

export const SpotifySubscriberAuthPage = () => {
    const context = useOutletContext();
    const navigate = useNavigate();
    const url = window.location.href;
    const spotifyAccessToken = url.split('#')[1].split('&')[0].split('=')[1];

    // TODO: If no context.visitorId in 10 seconds, error out.

    useEffect(() => {
        if (!context.visitorId) return;
        (async () => {
            const queueId = window.localStorage.getItem('__mixify_sqid');
            const queue = await subscribeToQueue(queueId, spotifyAccessToken, context.visitorId);
            if (!queue || !queue.name) {
                navigate('/');
                return;  // TODO: Display error.
            }
            navigate(`/queue/${queue.name}`);
        })();
    }, [context.visitorId]);

    window.document.title = 'Mixify – Spotify';
    return (
        <Paper
            shadow='xs'
            p='sm'
            sx={{ backgroundColor: '#2b2c3d' }}
            withBorder
            m={20}
        >
            <Center>
                <Stack align='center' spacing={10}>
                    <Text size='sm'>Authenticating user</Text>
                    <Loader />
                </Stack>
            </Center>
        </Paper>
    );
};