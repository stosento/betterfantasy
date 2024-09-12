export default function handler(request, response) {
    const authHeader = request.headers.get('authorization');
    if (
        !process.env.CRON_SECRET ||
        authHeader !== `Bearer ${process.env.CRON_SECRET}`
    ) {
        return response.status(401).json({ success: false });
    }

    response.status(200).json({ success: true });
}
