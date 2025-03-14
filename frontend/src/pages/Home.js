import { useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { Image, Title, PinInput, Group, Stack, Paper, Button, Badge, Text, Center, Space } from '@mantine/core';
import spotifyLogo from '../assets/spotify-logo.png';
import appleMusicLogo from '../assets/apple-music-logo.png';

export const HomePage = () => {
    const context = useOutletContext();
    const navigate = useNavigate();
    const [queueName, setQueueName] = useState('');
    let spotifyAuthUrl = `https://accounts.spotify.com/authorize?`;
    spotifyAuthUrl += `client_id=${process.env.REACT_APP_SPOTIFY_CLIENT_ID}`;
    spotifyAuthUrl += `&redirect_uri=${process.env.REACT_APP_SPOTIFY_HOST_REDIRECT_URI}`;
    spotifyAuthUrl += `&response_type=token&show_dialogue=true`;
    spotifyAuthUrl += `&scope=user-read-playback-state%2Cuser-modify-playback-state`
    spotifyAuthUrl += `%2Cuser-read-private%2Cuser-read-email`;

    window.document.title = 'Mixify – Home';
    return (
        <Stack align='stretch' p={20} pt={15}>
            <Paper
                shadow='xs'
                p='md'
                sx={{ backgroundColor: '#2b2c3d' }}
                withBorder
            >
                <Stack spacing={0}>
                    <Title order={4}>Host</Title>
                    <Text size='xs'>Connect through your streaming service</Text>
                    <Space h={15} />
                    <Button
                        color='dark'
                        radius='xl'
                        size='lg'
                        onClick={() => window.location.href = spotifyAuthUrl}
                        sx={{ backgroundColor: 'black' }}
                        mb={8}
                    >
                        <Group spacing={12}>
                            <Image maw={25} src={spotifyLogo} alt='spotify-logo' withPlaceholder />
                            <Text>Spotify</Text>
                        </Group>
                    </Button>
                    <Button color='dark' radius='xl' size='lg' disabled>
                        <Group spacing={12}>
                            <Image maw={25} src={appleMusicLogo} alt='apple-music-logo' opacity={0.5} withPlaceholder />
                            <Text>Apple Music</Text>
                            <Badge size='xs' variant='outline' color='green' mt={2}>Coming Soon</Badge>
                        </Group>
                    </Button>
                </Stack>
            </Paper>

            <Paper
                shadow='xs'
                p='md'
                sx={{ backgroundColor: '#2b2c3d' }}
                withBorder
            >
                <Stack spacing={0}>
                    <Title order={4}>Join</Title>
                    <Text size='xs'>Enter the 6 digit room name</Text>
                    <Space h={15} />
                    <Center mb={5}>
                        <PinInput
                            size='md'
                            value={queueName}
                            onChange={(value) => setQueueName(value.toUpperCase())}
                            length={6}
                            onComplete={() => navigate(`/queue/${queueName}`)}
                        />
                    </Center>
                </Stack>
            </Paper>
        </Stack>
    );
};