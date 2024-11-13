# import .env file and export it to the environment
include .env
export

.PHONY: frontend backend both start-telemetry

frontend:
	cd frontend && streamlit run app.py

backend:
	cd app && uvicorn main:app --reload

both:
	make -j2 frontend backend

start-telemetry:
	-docker compose down
	docker compose up -d
