import { useState, useEffect, useRef, useCallback } from 'react';
import client from '../api/client';

export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);
    const [isNotiOpen, setIsNotiOpen] = useState(false);
    const isMounted = useRef(false);

    const fetchNotifications = useCallback(async () => {
        try {
            const res = await client.get('/notifications');
            if (isMounted.current) {
                setNotifications(res.data);
            }
        } catch (e) {
            console.error("Polling Error:", e);
        }
    }, []);

    const markRead = async (id) => {
        try {
            await client.post(`/notifications/${id}/read`);
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: 1 } : n));
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        isMounted.current = true;
        fetchNotifications();

        // 30s Polling with recursive setTimeout to prevent overlap
        let timeoutId;
        const poll = async () => {
            await fetchNotifications();
            if (isMounted.current) {
                timeoutId = setTimeout(poll, 30000);
            }
        };

        timeoutId = setTimeout(poll, 30000);

        return () => {
            isMounted.current = false;
            clearTimeout(timeoutId);
        };
    }, [fetchNotifications]);

    return {
        notifications,
        isNotiOpen,
        setIsNotiOpen,
        markRead,
        refreshNotifications: fetchNotifications
    };
};
