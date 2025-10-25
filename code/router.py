@app.post("/process")
async def process_request(request: Request):
    # Create initial db record
    request_id = await db.create_request(params)

    try:
        # Start processing
        process_id = generate_process_id()  # Your logic here
        await db.start_processing(request_id, process_id)

        # Your processing logic here
        result = await process_request(request.data)

        # Store results
        await db.complete_processing(request_id, result)

        return {"status": "completed", "result": result}

    except Exception as e:
        await db.fail_processing(request_id, str(e))
        raise e
