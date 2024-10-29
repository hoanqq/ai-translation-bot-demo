.PHONY: frontend backend both

frontend:
	cd frontend && streamlit run app.py

backend:
	cd app && uvicorn main:app --reload

both:
	make -j2 frontend backend
