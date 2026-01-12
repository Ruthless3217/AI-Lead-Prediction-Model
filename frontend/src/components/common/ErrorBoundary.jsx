import React from 'react';
import { AlertCircle } from 'lucide-react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ errorInfo });
        // You can also log to an error reporting service here
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-[200px] w-full flex flex-col items-center justify-center p-8 bg-red-50 rounded-xl border border-red-200 text-center">
                    <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
                    <h2 className="text-xl font-bold text-red-700 mb-2">Something went wrong.</h2>
                    <p className="text-sm text-red-600 mb-4 max-w-md">
                        We're sorry, but the application encountered an unexpected error.
                    </p>
                    <details className="text-left bg-white p-4 rounded border border-red-100 text-xs text-slate-500 w-full max-w-lg overflow-auto">
                        <summary className="cursor-pointer font-medium mb-1 hover:text-red-600">View Error Details</summary>
                        <pre className="mt-2 whitespace-pre-wrap">
                            {this.state.error && this.state.error.toString()}
                            <br />
                            {this.state.errorInfo && this.state.errorInfo.componentStack}
                        </pre>
                    </details>
                    <button
                        onClick={() => window.location.reload()}
                        className="mt-6 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                    >
                        Reload Page
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
