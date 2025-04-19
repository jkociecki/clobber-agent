const ClobberSquare = ({ 
    row, 
    col, 
    piece, 
    isSelected, 
    isLegalMove, 
    onClick 
}) => {
    const getHighlightClass = () => {
        if (isSelected) {
            return 'border-4 border-yellow-500';
        }
        if (isLegalMove) {
            return 'border-4 border-green-500';
        }
        return '';
    };

    const isLightSquare = (row + col) % 2 === 0;
    const squareColor = isLightSquare ? 'bg-[#eeeed2]' : 'bg-[#769656]';

    const renderPiece = () => {
        if (!piece) return null;
        
        if (piece === 'white') {
            return (
                <div className="w-10 h-10 rounded-full bg-white border-2 border-gray-300 shadow-md"></div>
            );
        } else if (piece === 'black') {
            return (
                <div className="w-10 h-10 rounded-full bg-gray-800 border-2 border-gray-700 shadow-md"></div>
            );
        }
        
        return null;
    };

    return (
        <div
            className={`w-[75px] h-[75px] ${squareColor} ${getHighlightClass()} transition-colors duration-200 flex justify-center items-center cursor-pointer hover:opacity-90`}
            onClick={() => onClick(row, col)}
        >
            {renderPiece()}
        </div>
    );
};

export default ClobberSquare; 