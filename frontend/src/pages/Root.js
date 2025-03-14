import { Outlet, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import { Button, Container, Header, Group, Title, rem, Image, Popover, Stack, Text } from '@mantine/core';
import { IconFingerprint } from '@tabler/icons-react';
import mixifyLogoZoom from '../assets/mixify-logo-zoom.png';

export const RootPage = () => {
    const navigate = useNavigate();
    const [visitorId, setVisitorId] = useState('');
    const [balanceInfo, setBalanceInfo] = useState();
    const headerHeight = rem(60);

    useEffect(() => {
        (async () => {
            const fp = await FingerprintJS.load();
            const { visitorId } = await fp.get();
            setVisitorId(visitorId);
        })();
    }, []);

    return (
        <div>
            <Header height={headerHeight} sx={{ borderBottom: 0 }}>
                <Container
                    sx={{
                        height: headerHeight,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                    }}
                    fluid
                >
                    <Group
                        sx={{ cursor: 'pointer' }}
                        onClick={() => navigate('/')}
                        spacing={8}
                    >
                        <Image src={mixifyLogoZoom} radius='md' width={45} />
                        <Title order={2}>Mixify</Title>
                    </Group>
                    <Popover width={200} position='bottom-end' withArrow>
                        <Popover.Target>
                            <Button radius='xl' variant='gradient' size='sm' h={32} leftIcon={<IconFingerprint size={17} stroke={3} />}>
                                {!!visitorId ? visitorId.slice(0, 10) : `Loading...`}
                            </Button>
                        </Popover.Target>
                        {balanceInfo != null && (
                            <Popover.Dropdown>
                                <Stack spacing={5}>
                                    <Title order={5}>Your balance</Title>
                                    <Text size='lg'>{`$${balanceInfo.amount.toFixed(2)}`}</Text>
                                    {balanceInfo.amount > 0 && (
                                        <Text size='sm' fs='italic' c='dimmed' inline>{`${balanceInfo.boost_count} song${balanceInfo.boost_count === 1 ? ' was' : 's were'} boosted in ${balanceInfo.queue_count} of your rooms.`}</Text>
                                    )}
                                </Stack>
                            </Popover.Dropdown>
                        )}
                    </Popover>
                </Container>
            </Header>
            {!!visitorId && (
                <Outlet context={{ visitorId, setBalanceInfo }} />
            )}
        </div>
    );
};