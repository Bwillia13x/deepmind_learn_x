'use client';

interface LoadingSkeletonProps {
    className?: string;
    variant?: 'text' | 'card' | 'circle' | 'button';
    count?: number;
}

export function LoadingSkeleton({
    className = '',
    variant = 'text',
    count = 1
}: LoadingSkeletonProps) {
    const baseClasses = 'animate-pulse bg-gray-200 rounded';

    const variantClasses = {
        text: 'h-4 w-full',
        card: 'h-32 w-full rounded-lg',
        circle: 'h-12 w-12 rounded-full',
        button: 'h-10 w-24 rounded-lg',
    };

    return (
        <>
            {Array.from({ length: count }).map((_, i) => (
                <div
                    key={i}
                    className={`${baseClasses} ${variantClasses[variant]} ${className}`}
                />
            ))}
        </>
    );
}

export function CardSkeleton() {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4" />
            <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-full" />
                <div className="h-4 bg-gray-200 rounded w-5/6" />
                <div className="h-4 bg-gray-200 rounded w-4/6" />
            </div>
        </div>
    );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b bg-gray-50">
                <div className="h-6 bg-gray-200 rounded w-1/4 animate-pulse" />
            </div>
            <div className="divide-y divide-gray-100">
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="p-4 flex items-center space-x-4 animate-pulse">
                        <div className="h-10 w-10 bg-gray-200 rounded-full" />
                        <div className="flex-1 space-y-2">
                            <div className="h-4 bg-gray-200 rounded w-1/3" />
                            <div className="h-3 bg-gray-200 rounded w-1/4" />
                        </div>
                        <div className="h-8 w-20 bg-gray-200 rounded" />
                    </div>
                ))}
            </div>
        </div>
    );
}

export function DashboardSkeleton() {
    return (
        <div className="space-y-6">
            {/* Stats row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-1/2 mb-3" />
                        <div className="h-8 bg-gray-200 rounded w-3/4" />
                    </div>
                ))}
            </div>
            {/* Chart placeholder */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/4 mb-4" />
                <div className="h-48 bg-gray-200 rounded" />
            </div>
            {/* Table placeholder */}
            <TableSkeleton rows={3} />
        </div>
    );
}

export default LoadingSkeleton;
