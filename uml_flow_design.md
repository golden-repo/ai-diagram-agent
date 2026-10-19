# E-commerce Refund Logic
Show me the decision process as UML flowchart for a product return.

The process starts when a Customer submits a refund request. 
First, check if the item was purchased within 30 days. 
If no, reject the request. 
If yes, check if the item is damaged. 
If it is damaged, send it to the 'Quality Control' team. 
If it is not damaged, approve the refund and trigger a payment to the Customer.

Output: Mermaid
GenerateImage: Yes