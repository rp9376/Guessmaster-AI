class TwentyQuestionsGame {
    constructor() {
        this.messageHistory = [];  // Renamed to avoid conflict with DOM element
        this.questionCount = 0;
        this.isWaitingForResponse = false;
        this.currentEventSource = null;
        this.currentQuestionCounts = true;  // Track if current question should count
        
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        // Cards
        this.rulesCard = document.getElementById('rulesCard');
        this.gameInterface = document.getElementById('gameInterface');
        this.endGameScreen = document.getElementById('endGameScreen');
        
        // Buttons
        this.startGameBtn = document.getElementById('startGameBtn');
        this.yesBtn = document.getElementById('yesBtn');
        this.noBtn = document.getElementById('noBtn');
        this.dontKnowBtn = document.getElementById('dontKnowBtn');
        this.newGameBtn = document.getElementById('newGameBtn');
        this.playAgainBtn = document.getElementById('playAgainBtn');
        this.viewHistoryBtn = document.getElementById('viewHistoryBtn');
        this.hideHistoryBtn = document.getElementById('hideHistoryBtn');
        
        // Display elements
        this.aiQuestion = document.getElementById('aiQuestion');
        this.questionCounter = document.getElementById('questionCounter');
        this.conversationHistoryElement = document.getElementById('conversationHistory');
        this.endGameContent = document.getElementById('endGameContent');
        this.endGameHistory = document.getElementById('endGameHistory');
        this.endGameHistoryContent = document.getElementById('endGameHistoryContent');
    }

    bindEvents() {
        this.startGameBtn.addEventListener('click', () => this.startGame());
        this.yesBtn.addEventListener('click', () => this.answerQuestion('Yes'));
        this.noBtn.addEventListener('click', () => this.answerQuestion('No'));
        this.dontKnowBtn.addEventListener('click', () => this.answerQuestion("I don't know", false));
        this.newGameBtn.addEventListener('click', () => this.resetGame());
        this.playAgainBtn.addEventListener('click', () => this.resetGame());
        this.viewHistoryBtn.addEventListener('click', () => this.showGameHistory());
        this.hideHistoryBtn.addEventListener('click', () => this.hideGameHistory());
    }

    startGame() {
        console.log('🎮 Starting new game...');
        
        this.rulesCard.classList.add('hidden');
        this.gameInterface.classList.remove('hidden');
        
        this.resetGameState();
        this.askAI();
    }

    resetGameState() {
        this.messageHistory = [];
        this.questionCount = 0;
        this.isWaitingForResponse = false;
        this.updateQuestionCounter();
        this.clearConversationHistory();
        this.setButtonsEnabled(false);
    }

    resetGame() {
        console.log('🔄 Resetting game...');
        
        if (this.currentEventSource) {
            this.currentEventSource.close();
            this.currentEventSource = null;
        }
        
        // Hide all screens except rules
        this.gameInterface.classList.add('hidden');
        this.endGameScreen.classList.add('hidden');
        this.endGameHistory.classList.add('hidden');
        this.rulesCard.classList.remove('hidden');
        
        // Reset guess buttons
        this.hideGuessButtons();
        
        this.resetGameState();
    }

    async askAI(countsAsQuestion = true) {
        if (this.isWaitingForResponse) {
            console.log('⏳ Already waiting for AI response...');
            return;
        }

        this.isWaitingForResponse = true;
        this.setButtonsEnabled(false);
        this.showTypingIndicator();

        console.log('🤖 Sending request to AI...');
        console.log('📝 Current conversation history:', this.messageHistory);

        // Store whether this should count as a question for later use
        this.currentQuestionCounts = countsAsQuestion;

        try {
            // Close any existing EventSource
            if (this.currentEventSource) {
                this.currentEventSource.close();
            }

            // Create EventSource for streaming
            const response = await fetch('/api/ask/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    history: this.messageHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiResponse = '';

            this.hideTypingIndicator();

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            this.handleAIResponseComplete(aiResponse);
                            return;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            
                            if (parsed.type === 'debug') {
                                console.log('🔍 DEBUG - Full prompt sent to LLM:', parsed.full_prompt);
                                console.log('🔍 DEBUG - Full AI response:', parsed.full_response);
                            } else if (parsed.content) {
                                aiResponse += parsed.content;
                                this.updateAIQuestion(aiResponse);
                            }
                        } catch (e) {
                            // Ignore JSON parse errors for streaming chunks
                        }
                    }
                }
            }

        } catch (error) {
            console.error('❌ Error communicating with AI:', error);
            this.handleError(error.message);
        }
    }

    handleAIResponseComplete(response) {
        console.log('✅ AI response complete:', response);
        
        // Add AI response to conversation history
        this.messageHistory.push({
            role: 'assistant',
            content: response
        });

        // Only increment question count if the previous user response counted as a question
        if (this.currentQuestionCounts) {
            this.questionCount++;
            console.log(`📊 Question count: ${this.questionCount}/20`);
        } else {
            console.log('📊 Question count unchanged (previous response was "I don\'t know")');
        }
        
        this.updateQuestionCounter();
        this.addToConversationHistory('AI', response, 'ai');

        // Check if AI made a guess (contains "Is it" pattern)
        const isGuess = this.detectAIGuess(response);
        
        this.isWaitingForResponse = false;
        
        // If it's a guess, show special guess buttons, otherwise show normal buttons
        if (isGuess) {
            console.log('🎯 AI made a guess! Showing guess response buttons...');
            this.showGuessButtons();
        } else {
            this.setButtonsEnabled(true);
        }

        // Check if game should end due to question limit
        if (this.questionCount >= 20 && !isGuess) {
            this.endGame('questionsExhausted');
        }
    }

    answerQuestion(answer, countsAsQuestion = true) {
        if (this.isWaitingForResponse) {
            console.log('⏳ Please wait for AI response...');
            return;
        }

        console.log(`👤 User answered: ${answer}`);
        
        if (!countsAsQuestion) {
            console.log('💡 This response does not count against the question limit');
        }

        // Add user response to conversation history
        this.messageHistory.push({
            role: 'user',
            content: answer
        });

        this.addToConversationHistory('You', answer, 'user');

        // Ask AI for next question
        this.askAI(countsAsQuestion);
    }

    showTypingIndicator() {
        this.aiQuestion.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
    }

    hideTypingIndicator() {
        // Will be replaced by updateAIQuestion
    }

    updateAIQuestion(text) {
        this.aiQuestion.textContent = text;
    }

    updateQuestionCounter() {
        this.questionCounter.textContent = this.questionCount;
        
        // Add visual warning when approaching limit
        if (this.questionCount >= 18) {
            this.questionCounter.classList.add('text-red-600');
            this.questionCounter.classList.remove('text-purple-600');
        } else if (this.questionCount >= 15) {
            this.questionCounter.classList.add('text-orange-600');
            this.questionCounter.classList.remove('text-purple-600');
        }
    }

    addToConversationHistory(speaker, message, type) {
        const historyItem = document.createElement('div');
        historyItem.className = `message-bubble p-3 rounded-lg ${
            type === 'ai' ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-green-50 border-l-4 border-green-400'
        }`;
        
        historyItem.innerHTML = `
            <div class="flex items-start space-x-3">
                <span class="text-lg">${type === 'ai' ? '🤖' : '👤'}</span>
                <div>
                    <strong class="text-gray-800">${speaker}:</strong>
                    <span class="text-gray-700 ml-2">${message}</span>
                </div>
            </div>
        `;

        this.conversationHistoryElement.appendChild(historyItem);
        this.conversationHistoryElement.scrollTop = this.conversationHistoryElement.scrollHeight;
    }

    clearConversationHistory() {
        this.conversationHistoryElement.innerHTML = '';
    }

    setButtonsEnabled(enabled) {
        this.yesBtn.disabled = !enabled;
        this.noBtn.disabled = !enabled;
        this.dontKnowBtn.disabled = !enabled;
        
        if (enabled) {
            this.yesBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            this.noBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            this.dontKnowBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            this.yesBtn.classList.add('opacity-50', 'cursor-not-allowed');
            this.noBtn.classList.add('opacity-50', 'cursor-not-allowed');
            this.dontKnowBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    endGame(reason = 'questionsExhausted') {
        console.log(`🏁 Game ended - reason: ${reason}`);
        
        this.setButtonsEnabled(false);
        
        // Hide game interface and show end screen
        this.gameInterface.classList.add('hidden');
        this.endGameScreen.classList.remove('hidden');
        
        // Set end game content based on reason
        if (reason === 'questionsExhausted') {
            this.endGameContent.innerHTML = `
                <div class="text-center">
                    <span class="text-6xl mb-4 block">🏁</span>
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">Game Over!</h2>
                    <p class="text-xl text-gray-600 mb-4">The AI used all 20 questions.</p>
                    <p class="text-lg text-gray-700">Did the AI guess what you were thinking of?</p>
                </div>
            `;
        } else if (reason === 'aiGuessedCorrect') {
            this.endGameContent.innerHTML = `
                <div class="text-center">
                    <span class="text-6xl mb-4 block">�</span>
                    <h2 class="text-3xl font-bold text-green-600 mb-4">AI Wins!</h2>
                    <p class="text-xl text-gray-600 mb-4">The AI successfully guessed what you were thinking!</p>
                    <p class="text-lg text-gray-700">Questions used: ${this.questionCount}/20</p>
                </div>
            `;
        } else if (reason === 'aiGuessedWrong') {
            this.endGameContent.innerHTML = `
                <div class="text-center">
                    <span class="text-6xl mb-4 block">🎊</span>
                    <h2 class="text-3xl font-bold text-blue-600 mb-4">You Win!</h2>
                    <p class="text-xl text-gray-600 mb-4">The AI's guess was incorrect!</p>
                    <p class="text-lg text-gray-700">You stumped the AI in ${this.questionCount} questions!</p>
                </div>
            `;
        }
    }

    detectAIGuess(response) {
        // Look for patterns that indicate the AI is making a guess
        const guessPatterns = [
            /is it .+\?/i,
            /are you thinking of .+\?/i,
            /could it be .+\?/i,
            /my guess is .+/i,
            /i think it'?s .+/i,
            /final guess:? .+/i
        ];
        
        return guessPatterns.some(pattern => pattern.test(response));
    }

    showGuessButtons() {
        // Hide normal answer buttons
        this.yesBtn.style.display = 'none';
        this.noBtn.style.display = 'none';
        this.dontKnowBtn.style.display = 'none';
        
        // Create guess response buttons if they don't exist
        if (!document.getElementById('correctGuessBtn')) {
            const buttonContainer = this.yesBtn.parentNode;
            
            const correctBtn = document.createElement('button');
            correctBtn.id = 'correctGuessBtn';
            correctBtn.className = 'bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-8 rounded-xl text-xl transition-all duration-300 transform hover:scale-105 shadow-lg';
            correctBtn.innerHTML = '🎯 Correct!';
            correctBtn.onclick = () => this.handleGuessResponse(true);
            
            const wrongBtn = document.createElement('button');
            wrongBtn.id = 'wrongGuessBtn';
            wrongBtn.className = 'bg-red-500 hover:bg-red-600 text-white font-bold py-4 px-8 rounded-xl text-xl transition-all duration-300 transform hover:scale-105 shadow-lg ml-4';
            wrongBtn.innerHTML = '❌ Wrong!';
            wrongBtn.onclick = () => this.handleGuessResponse(false);
            
            buttonContainer.appendChild(correctBtn);
            buttonContainer.appendChild(wrongBtn);
        } else {
            // Show existing guess buttons
            document.getElementById('correctGuessBtn').style.display = 'inline-block';
            document.getElementById('wrongGuessBtn').style.display = 'inline-block';
        }
    }

    hideGuessButtons() {
        // Show normal answer buttons
        this.yesBtn.style.display = 'inline-block';
        this.noBtn.style.display = 'inline-block';
        this.dontKnowBtn.style.display = 'inline-block';
        
        // Hide guess buttons
        const correctBtn = document.getElementById('correctGuessBtn');
        const wrongBtn = document.getElementById('wrongGuessBtn');
        if (correctBtn) correctBtn.style.display = 'none';
        if (wrongBtn) wrongBtn.style.display = 'none';
    }

    handleGuessResponse(isCorrect) {
        console.log(`🎯 User responded to guess: ${isCorrect ? 'Correct' : 'Wrong'}`);
        
        // Add the response to conversation history
        const response = isCorrect ? 'Yes, that\'s correct!' : 'No, that\'s wrong.';
        this.messageHistory.push({
            role: 'user',
            content: response
        });
        
        this.addToConversationHistory('You', response, 'user');
        
        // End the game with appropriate reason
        if (isCorrect) {
            this.endGame('aiGuessedCorrect');
        } else {
            this.endGame('aiGuessedWrong');
        }
    }

    showGameHistory() {
        this.endGameHistoryContent.innerHTML = '';
        
        // Populate history
        this.messageHistory.forEach((msg, index) => {
            const historyItem = document.createElement('div');
            const isAI = msg.role === 'assistant';
            historyItem.className = `p-3 rounded-lg ${
                isAI ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-green-50 border-l-4 border-green-400'
            }`;
            
            historyItem.innerHTML = `
                <div class="flex items-start space-x-3">
                    <span class="text-lg">${isAI ? '🤖' : '👤'}</span>
                    <div>
                        <strong class="text-gray-800">${isAI ? 'AI' : 'You'}:</strong>
                        <span class="text-gray-700 ml-2">${msg.content}</span>
                    </div>
                </div>
            `;
            
            this.endGameHistoryContent.appendChild(historyItem);
        });
        
        this.endGameHistory.classList.remove('hidden');
    }

    hideGameHistory() {
        this.endGameHistory.classList.add('hidden');
    }

    handleError(errorMessage) {
        console.error('❌ Game error:', errorMessage);
        
        this.aiQuestion.innerHTML = `
            <div class="text-red-600">
                <span class="text-xl">⚠️</span>
                Error: ${errorMessage}
                <br>
                <button class="text-blue-600 underline mt-2" onclick="location.reload()">
                    Try refreshing the page
                </button>
            </div>
        `;
        
        this.isWaitingForResponse = false;
        this.setButtonsEnabled(false);
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 GuessMaster 20Q loaded!');
    window.game = new TwentyQuestionsGame();
});
