// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract MedFeedback {
    struct Feedback {
        string query;
        string modelResponse;
        string correctedResponse;
        string clinicianName;
        uint8 score;  // Score (0-6)
        uint timestamp;
    }

    Feedback[] public feedbackList;
    address public owner;

    event FeedbackSubmitted(
        uint indexed feedbackId,
        string query,
        string modelResponse,
        string correctedResponse,
        string clinicianName,
        uint8 score,
        uint timestamp
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    function submitFeedback(
        string memory _query,
        string memory _modelResponse,
        string memory _correctedResponse,
        string memory _clinicianName,
        uint8 _score
    ) public {
        require(_score <= 6, "Score must be between 0 and 6");
        require(bytes(_query).length > 0, "Query cannot be empty");
        require(bytes(_correctedResponse).length > 0, "Corrected response cannot be empty");

        Feedback memory newFeedback = Feedback({
            query: _query,
            modelResponse: _modelResponse,
            correctedResponse: _correctedResponse,
            clinicianName: _clinicianName,
            score: _score,
            timestamp: block.timestamp
        });

        feedbackList.push(newFeedback);

        emit FeedbackSubmitted(feedbackList.length - 1, _query, _modelResponse, _correctedResponse, _clinicianName, _score, block.timestamp);
    }

    function getFeedback(uint index) public view returns (
        string memory, string memory, string memory, string memory, uint8, uint
    ) {
        require(index < feedbackList.length, "Invalid index");
        Feedback storage f = feedbackList[index];
        return (f.query, f.modelResponse, f.correctedResponse, f.clinicianName, f.score, f.timestamp);
    }

    function getFeedbackCount() public view returns (uint) {
        return feedbackList.length;
    }

    function clearFeedback() public onlyOwner {
        delete feedbackList;
    }
}
